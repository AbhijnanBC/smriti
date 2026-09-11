"""
test_config_single_source.py — P0-7 (external "reality check" review).

Prior to this fix, config/default.yaml had two sections for each of
embedding and NLI config: "embedding" / "embedding_phase5", and
"nli" / "nli_phase6". The code consistently read keys ("model_name",
"device", "batch_size") that existed only in the section it did NOT
read from, so editing the documented "embedding.model" / "nli.model"
keys had zero effect on runtime behavior -- a config file that claimed
to be the single source of truth, silently, was not one.

These tests check two things a reviewer would actually ask:
  1. Static contract: the shipped default.yaml has exactly the keys the
     code reads, under the section the code reads, and the dead
     duplicate sections are gone.
  2. Runtime effect: changing a config value actually changes what the
     consuming class does, for real component code (not a reimplemented
     stand-in), with the underlying ML model call mocked so this stays a
     fast, offline unit test.
"""

from __future__ import annotations

import numpy as np
import pytest
from smriti.core.config import get_config


@pytest.fixture
def real_config_data():
    return get_config()._data


class TestDefaultYamlStaticContract:
    def test_embedding_section_has_the_keys_the_code_reads(self, real_config_data):
        emb = real_config_data.get("embedding", {})
        assert "model_name" in emb, (
            "embedder.py reads emb_cfg.get('model_name', ...) -- the config "
            "section must use that exact key, not 'model'."
        )
        assert "device" in emb
        assert "batch_size" in emb

    def test_nli_section_has_the_keys_the_code_reads(self, real_config_data):
        nli = real_config_data.get("nli", {})
        assert "model_name" in nli, (
            "evidence.py/resolver.py/replay.py read nli_cfg.get('model_name', "
            "...) -- the config section must use that exact key, not 'model'."
        )
        assert "batch_size" in nli

    def test_dead_duplicate_sections_are_gone(self, real_config_data):
        assert "embedding_phase5" not in real_config_data, (
            "embedding_phase5 duplicated 'embedding' and was never read by "
            "any code path -- it must not exist, not just be unread."
        )
        assert "nli_phase6" not in real_config_data, (
            "nli_phase6 duplicated 'nli' and was never read by any code "
            "path -- it must not exist, not just be unread."
        )

    def test_priority_order_is_a_single_canonical_list(self, real_config_data):
        order = real_config_data["resolver_policy"]["priority_order"]
        assert set(order) == {
            "contradicts",
            "equivalent",
            "supports",
            "refines",
            "neutral",
            "unknown",
        }


class TestRuntimeConfigEffect:
    """Changing a config value must change what the real component does,
    not just what a test's own mock says it should do."""

    def test_changing_embedding_model_name_changes_what_sentencetransformer_is_asked_to_load(
        self, monkeypatch
    ):
        import smriti.embedding.embedder as embedder_module

        captured = {}

        class FakeSentenceTransformer:
            def __init__(self, model_name, device=None):
                captured["model_name"] = model_name
                captured["device"] = device

            def encode(self, texts, convert_to_numpy=True):
                return np.zeros((len(texts), 384))

            def __getitem__(self, idx):
                raise IndexError("no wrapped HF model in this fake")

        monkeypatch.setattr(
            "sentence_transformers.SentenceTransformer", FakeSentenceTransformer, raising=False
        )

        fake_config = {
            "embedding": {"model_name": "a-totally-different-model/xyz", "device": "cpu"}
        }
        monkeypatch.setattr(embedder_module, "get_config", lambda: FakeConfig(fake_config))

        emb = embedder_module.SentenceTransformerEmbedder()
        assert captured["model_name"] == "a-totally-different-model/xyz", (
            "Changing config['embedding']['model_name'] must change the model "
            "name actually passed to SentenceTransformer(); it did not, which "
            "is exactly the P0-7 defect."
        )
        assert emb.descriptor.model_name == "a-totally-different-model/xyz"

    def test_changing_nli_model_name_changes_what_crossencoder_is_asked_to_load(self, monkeypatch):
        import smriti.retrieval.classification.evidence as evidence_module

        captured = {}

        class FakeCrossEncoder:
            def __init__(self, model_name):
                captured["model_name"] = model_name
                self.model = type("M", (), {"config": None})()

            def predict(self, pairs, apply_softmax=True, convert_to_numpy=True, batch_size=16):
                return np.tile(np.array([0.1, 0.8, 0.1]), (len(pairs), 1))

        monkeypatch.setattr("sentence_transformers.CrossEncoder", FakeCrossEncoder, raising=False)
        monkeypatch.setattr(
            evidence_module, "resolve_hf_revision", lambda hf_config, model_name: "fake-revision"
        )

        fake_config = {"nli": {"model_name": "a-totally-different-nli-model/xyz", "batch_size": 4}}
        monkeypatch.setattr(evidence_module, "get_config", lambda: FakeConfig(fake_config))

        gen = evidence_module.NLIEvidenceGenerator()
        assert captured["model_name"] == "a-totally-different-nli-model/xyz", (
            "Changing config['nli']['model_name'] must change the model name "
            "actually passed to CrossEncoder(); it did not, which is exactly "
            "the P0-7 defect."
        )
        assert gen._batch_size == 4, (
            "Changing config['nli']['batch_size'] must change the batch size "
            "the generator actually uses -- previously always defaulted to "
            "16 because the real value lived only in the dead 'nli_phase6' "
            "section."
        )


class FakeConfig:
    """Minimal stand-in for smriti.core.config.Config exposing only .get()."""

    def __init__(self, data: dict):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)

# SMRITI-Reference Vault Manifest

**RECTIFIED (external "reality check" review round 3, P1 "_MANIFEST.md
is contaminating the baseline"):** relocated from
`data/raw/reference_vault/_MANIFEST.md` to this file. That directory is
scanned directly by both the real pipeline (Phase 1 discovery) and the
naive-extraction baseline (`scripts/run_baselines.py`) -- the assertion
classifier correctly discards this file's content as non-declarative
metadata in the real pipeline (0 of 397 Phase 4 claims trace to it), but
the naive baseline has no such classifier and extracted 63 spurious
"claims" from this manifest's own list lines, inflating its reported
690-claim total by about 9%. Renamed from "SMRITI-Gold" to
"SMRITI-Reference" for the same reason the vault directory itself was
renamed (see README.md) -- this corpus's labels are LLM-derived, not
human-annotated ground truth.

- A1 [Technical] -> A1_ROS_2_Navigation_Stack_(Nav2)_Configurat.md
- A2 [Technical] -> A2_Gazebo_Harmonic_Physics_Simulation_Envir.md
- A3 [Technical] -> A3_ROS_2_and_Gazebo_Integration_for_Robotic.md
- A4 [Technical] -> A4_HDFS_Block_Storage_Architecture.md
- A5 [Technical] -> A5_HDFS_Federation_and_Namespace_Scaling.md
- A6 [Technical] -> A6_Apache_Hive_Data_Warehousing_with_Tez_Ex.md
- A7 [Technical] -> A7_Apache_Flume_Event_Stream_Processing.md
- A8 [Technical] -> A8_PySpark_RDD_In-Memory_Processing.md
- A9 [Technical] -> A9_Apache_Spark_RDD_Persistence_and_Fault_T.md
- A10 [Technical] -> A10_VirtualBox_Bridged_Networking_Configurat.md
- B1 [Scientific] -> B1_StyleGAN2_--_Improvements_in_Generative_.md
- B2 [Scientific] -> B2_StyleGAN2_Style_Space_Analysis_and_Disen.md
- B3 [Scientific] -> B3_WGAN-GP_Wasserstein_GAN_with_Gradient_P.md
- B4 [Scientific] -> B4_WGAN-GP_Applications_in_Image_Restoratio.md
- B5 [Scientific] -> B5_U-Net_Convolutional_Network_for_Medical.md
- B6 [Scientific] -> B6_U-Nets_Evolution_in_Medical_Imaging.md
- B7 [Scientific] -> B7_Kannada_Script_Formation_of_Ottakshara_.md
- B8 [Scientific] -> B8_Grammatical_Structure_of_Kannada_Conjunc.md
- B9 [Scientific] -> B9_Mobile_Robot_Kinematics_Coordinate_Tran.md
- B10 [Scientific] -> B10_Differential-Drive_Mobile_Robot_Kinemati.md
- B11 [Scientific] -> B11_Critique_of_U-Net_Transformers_Outperfo.md
- C1 [Analytical] -> C1_IPL_2026_RCBs_Defensive_Championship_C.md
- C2 [Analytical] -> C2_IPL_2025_The_Rise_of_Wrist-Spinners.md
- C3 [Analytical] -> C3_Tactical_Role_of_Wrist-Spinners_in_T20_C.md
- C4 [Analytical] -> C4_Evolution_of_Spin_Bowling_Strategies_in_.md
- C5 [Analytical] -> C5_Spin_Bowling_Techniques,_Strategies,_and.md
- C6 [Analytical] -> C6_IPL_Team_Composition_and_Tactical_Weakne.md
- C7 [Analytical] -> C7_Tactical_Resilience_of_Mystery_Spinners_.md
- C8 [Analytical] -> C8_Leg-Spin_Field_Placement_Strategies_in_C.md
- C9 [Analytical] -> C9_The_Rise_of_Left-Arm_Wrist-Spinners_in_I.md
- C10 [Analytical] -> C10_IPL_2026_Team_Squad_Analysis_and_Key_Pla.md
- C11 [Analytical] -> C11_The_Case_Against_Wrist-Spinners_in_T20.md
- D1 [Procedural] -> D1_Pressure_Cooker_Lamb_Rogan_Josh.md
- D2 [Procedural] -> D2_Lamb_Rogan_Josh_--_Licious_Version.md
- D3 [Procedural] -> D3_Pressure_Cooker_Rogan_Josh_--_Art_of_Pal.md
- D4 [Procedural] -> D4_Pressure_Cooker_Rogan_Josh_--_Key_Techni.md
- D5 [Procedural] -> D5_Raw_Mango_Prawn_Curry_--_Sanjeev_Kapoor_.md
- D6 [Procedural] -> D6_Raw_Mango_Prawn_Curry_--_SideChef_Versio.md
- D7 [Procedural] -> D7_Kerala-Style_Raw_Mango_Prawn_Curry.md
- D8 [Procedural] -> D8_Malabar-Style_Raw_Mango_Prawn_Curry.md
- D9 [Procedural] -> D9_Kerala_Drumstick_Raw_Mango_Prawns_Curry.md
- D10 [Procedural] -> D10_Raw_Mango_Prawn_Curry_--_Plating_and_Ser.md
- D11 [Procedural] -> D11_Pressure_Cooking_Ruins_Lamb_Rogan_Josh.md
- E1 [Encyclopedic] -> E1_Overview_of_the_Solar_System.md
- E2 [Encyclopedic] -> E2_Earth_The_Third_Planet_from_the_Sun.md
- E3 [Encyclopedic] -> E3_Earths_Orbital_and_Physical_Characteris.md
- E4 [Encyclopedic] -> E4_Formation_and_Evolution_of_the_Solar_Sys.md
- E5 [Encyclopedic] -> E5_Classification_of_Planets_in_the_Solar_S.md
- E6 [Encyclopedic] -> E6_Earths_Density_and_Mass.md
- E7 [Encyclopedic] -> E7_The_Suns_Dominance_in_the_Solar_System.md
- E8 [Encyclopedic] -> E8_Boundaries_and_Structure_of_the_Solar_Sy.md
- E9 [Encyclopedic] -> E9_Minor_Bodies_in_the_Solar_System.md
- E10 [Encyclopedic] -> E10_Earth_as_a_Habitable_Planet.md

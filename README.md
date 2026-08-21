# LunarHabitatAI
AI-assisted lunar habitat site selection and mission decision-support software.

## Blockchain Provenance Layer

This project features a blockchain-backed provenance layer. After computational artifacts (ML models, AHP configurations, XAI outputs) are generated, their cryptographic fingerprints (hashes) are registered onto an Ethereum-compatible smart contract to ensure the integrity of the data. 

### Key Concepts
- **Data Provenance**: Proving that the final AI site decision is based strictly on unaltered original data, valid ML models, and pristine AHP results.
- **On-Chain vs Off-Chain Storage**: The blockchain does *not* store large datasets like the 160,000 grid cells, images, or large JSON files. Instead, it stores lightweight SHA-256 hashes on-chain. Off-chain data is canonicalized, hashed, and verified against the on-chain registry.
- **Tamper Detection**: If any result file (e.g. `score_breakdown.json`) is modified after the decision is registered, the local hash re-calculation will fail to match the blockchain record, instantly detecting the tampering.
- **Deterministic JSON**: All JSON artifacts are parsed, recursively sorted by keys, and serialized without spaces before hashing to ensure perfectly matching hashes across different systems.

### Directory Structure & Files
The `blockchain` module contains the Python logic and the Hardhat configuration:
- `blockchain/hardhat/contracts/LunarDecisionRegistry.sol`: Minimal Solidity smart contract containing the registry structure.
- `blockchain/hardhat/hardhat.config.js`: Configuration for the local Hardhat testing node.
- `blockchain/config.py`: Loads the `.env` settings dynamically (RPC URL, Private Key, Contract Address).
- `blockchain/hashing.py`: Contains standard cryptographic SHA-256 functions for files and deterministic JSON serialization.
- `blockchain/manifest.py`: Packages 12 key artifacts (Dataset, Preprocessing, ML Model, AHP Results, XAI outputs) into a unified `DecisionManifest`.
- `blockchain/registry.py`: The `web3.py` interface that connects to Ethereum/Hardhat, deploys the contract, and executes the `registerDecision` and `getDecision` methods.
- `blockchain/verifier.py`: The core verification engine that re-hashes the local files and compares them against the on-chain metadata.
- `blockchain/passport.py`: Generates the Human-Readable HTML "Decision Passport" (`decision_passport_Haworth_Crater.html`).

### Walkthrough & Hackathon Demo

The system provides a comprehensive demo script to demonstrate the tamper-evident architecture.

**Quick Start (For Hackathon Demo)**
1. Start the local node in a new terminal:
   ```bash
   cd blockchain/hardhat
   npx hardhat node
   ```
2. In your main terminal, run the demo:
   ```bash
   python -m blockchain.demo
   ```

**What the demo does:**
1. **Creation**: The contract is deployed to your local node, and a `DEC-2026-XXXX` manifest is generated for Haworth Crater based on the current AHP/ML outputs.
2. **Registration**: The SHA-256 hashes are successfully stored on-chain.
3. **Verification (PASS)**: Initial verification passes successfully for all 12 artifacts.
4. **Tampering**: The local AHP `score_breakdown.json` is deliberately modified in the script.
5. **Verification (FAIL)**: The tamper-detection engine catches the mismatch immediately:
    ```
    AHP Result                [FAIL] HASH MISMATCH
      Expected (Blockchain): 0x1c43...
      Actual (Local)       : 0x3f75...
    ```
6. **Restoration**: The original AHP file is restored, and verification passes again.

### Future Radiation Integration Compatibility
The `DecisionRecord` struct includes an open `modelHash` and `featureConfigHash` structure. When radiation fields are introduced in a future ML v2.0 update, the pipeline version simply increments. The new canonical JSON of the feature configuration will hash to a new distinct fingerprint without breaking or invalidating past v1.0 decisions.

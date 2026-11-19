# Production Data Requirements & Implementation Roadmap

## For: AI Parts Recommendation System — Moving from Prototype to Production

---

## Section 1: Data Required (6 Categories)

The prototype currently runs on 30 synthetic records. For production-grade accuracy (85%+ first-time fix rate), the system needs **real data across 6 categories**. Each category is explained below with the exact fields required.

---

### Category 1: Historical Service / Repair Records (MOST CRITICAL)

This is the single most important dataset. It is the "memory" of the entire system — the FAISS vector store is built from this data, and the AI's prediction accuracy is directly proportional to the quality and volume of these records.

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `case_id` | String | `SR-2024-00451` | Unique identifier for each service request |
| `complaint_text` | Text | "AC not cooling, making clicking sound" | The raw customer complaint — this gets embedded into vectors |
| `product_type` | String | "HVAC", "Refrigerator" | Filters similar cases by product family |
| `model` | String | "AC-22R" | Exact model for BOM matching |
| `serial_number` | String | "SN-89234" | Links to specific asset's service history |
| `symptoms` | List | ["not_cooling", "clicking_noise"] | Structured symptom tags for precise vector matching |
| `error_codes` | List | ["E205", "E102"] | Machine-reported diagnostic codes |
| `parts_replaced` | List | ["compressor", "thermostat"] | **Ground truth** — what the technician actually used |
| `primary_part` | String | "compressor" | The main part that fixed the issue |
| `fix_successful` | Boolean | true / false | Did the repair actually solve the problem? |
| `first_time_fix` | Boolean | true / false | Was it fixed in a single visit? |
| `resolution_time_hours` | Number | 4.5 | How long the repair took |
| `technician_id` | String | "TECH-042" | Which technician performed the repair |
| `technician_notes` | Text | "Compressor winding shorted..." | Free-text expert observations — rich context for RAG |
| `root_cause` | String | "compressor_wear" | The diagnosed root cause |
| `complaint_date` | Date | "2024-03-15" | When the complaint was registered |
| `resolution_date` | Date | "2024-03-17" | When it was resolved |
| `customer_region` | String | "South India" | Geographic context (climate affects failures) |
| `customer_satisfaction` | Number | 4 (out of 5) | Post-repair customer rating |

> **Minimum Volume Required:** 500+ records to start seeing meaningful accuracy. 2,000+ records for production-grade results. 10,000+ for enterprise-level performance.

> **Critical Rule:** Every record MUST have the `parts_replaced` field filled accurately. This is the "answer key" that the AI learns from. If this field is empty or inaccurate, the entire system breaks down.

---

### Category 2: Product / Asset Master Data

This tells the AI what parts exist inside each product model, what commonly fails, and what the known manufacturing issues are.

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `model` | String | "RF-28X" | Links to complaints and inventory |
| `product_type` | String | "Refrigerator" | Product family classification |
| `manufacturer` | String | "CoolTech Industries" | Manufacturer identification |
| `bom_parts` | List | ["compressor", "thermostat", "evaporator_coil", ...] | Bill of Materials — all parts inside the product |
| `common_failure_parts` | List | ["compressor", "thermostat"] | Parts known to fail frequently |
| `avg_lifespan_years` | Number | 12 | Expected product lifetime |
| `warranty_years` | Number | 3 | Warranty period |
| `known_issues` | List | ["Compressor fails after 4-5 years"] | Manufacturer-documented failure patterns |
| `manufacturing_batch` | String | "2023-Q2" | Batch-specific defect tracking |

> **Why This Matters:** When the AI predicts parts, it cross-checks against the BOM to make sure the predicted part actually exists in that product model. Without BOM data, the AI might predict a "drain pump" for a refrigerator (which doesn't have one).

---

### Category 3: Parts Inventory Data (Real-Time or Daily Sync)

This powers Agent 4 (Supply Decision). Without accurate stock data, the system can't decide whether to auto-order, reserve, or escalate.

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `part_id` | String | "P-101" | SKU identifier for warehouse systems |
| `part_name` | String | "compressor" | Human-readable part name |
| `part_description` | String | "Hermetic Reciprocating Compressor 1.5HP" | Detailed technical specification |
| `compatible_models` | List | ["RF-28X", "RF-22S"] | Which product models this part fits |
| `stock_quantity` | Number | 15 | Current units available |
| `warehouse_location` | String | "Delhi DC" | Where the stock is physically located |
| `unit_cost` | Number | 4500 | Cost per unit (in local currency) |
| `substitute_part_id` | String | "P-102" | Alternative part if this one is out of stock |
| `lead_time_days` | Number | 2 | Days to procure if out of stock |
| `reorder_point` | Number | 5 | Minimum stock level before reorder triggers |
| `part_image_url` | String | "https://..." | Image of the part for technician verification |

> **Critical Requirement:** This data must be **refreshed frequently** (ideally real-time API, minimum daily CSV sync). Stale inventory data = technician arrives and part isn't actually available.

---

### Category 4: Customer / Asset Installation Data

This tells the system the history and context of each specific installed unit.

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `asset_id` | String | "ASSET-7823" | Unique identifier for each installed unit |
| `customer_id` | String | "CUST-4521" | Links to customer account |
| `model` | String | "AC-22R" | Which product model is installed |
| `serial_number` | String | "SN-89234" | Exact unit identifier |
| `installation_date` | Date | "2021-06-15" | When it was installed (age = failure risk) |
| `location_region` | String | "Chennai, Tamil Nadu" | Geographic location (humidity, temperature) |
| `service_history_count` | Number | 3 | How many times this unit has been serviced |
| `last_service_date` | Date | "2024-01-10" | When it was last serviced |
| `warranty_status` | String | "Active" / "Expired" | Current warranty status |
| `maintenance_contract` | String | "AMC-Gold" | Type of maintenance agreement |

> **Why This Matters:** A 2-year-old AC in Chennai (high humidity) fails differently than a 7-year-old AC in Shimla (cold climate). The AI needs this context to adjust predictions. Also, if the same unit has been serviced 5 times for the same issue, the AI should escalate to a senior engineer instead of predicting the same part again.

---

### Category 5: Technician Master Data

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `technician_id` | String | "TECH-042" | Unique identifier |
| `name` | String | "Rajesh Kumar" | For assignment and reporting |
| `specialization` | List | ["HVAC", "Refrigerator"] | What product types they're trained on |
| `region` | String | "South Zone" | Their assigned service territory |
| `skill_level` | String | "Senior" / "Junior" | Experience level |
| `avg_first_time_fix_rate` | Number | 0.82 | Historical FTF rate — helps route complex cases to experienced technicians |

---

### Category 6: Error Code Dictionary

A mapping of machine error codes to human-readable descriptions and commonly associated parts.

| Field | Type | Example | Why It's Needed |
|---|---|---|---|
| `error_code` | String | "E205" | The code displayed on the machine |
| `description` | String | "Thermostat sensor out of range" | What the code means |
| `applicable_models` | List | ["AC-22R", "AC-30S"] | Which models generate this code |
| `commonly_associated_parts` | List | ["thermostat", "control_board"] | Parts typically linked to this error |
| `severity` | String | "High" | Urgency level of this error |

> **Why This Matters:** Error codes are the most precise diagnostic signal. If the customer reports "E205", the AI should immediately know it's a thermostat issue with 90%+ confidence — far more accurate than relying on the customer's description alone.

---

## Section 2: Approach After Receiving the Data

### Phase 1: Data Cleaning & Validation (Week 1-2)

| Task | Details |
|---|---|
| Remove duplicates | Same case logged twice in different systems |
| Handle missing values | Records where `parts_replaced` is empty are useless — flag or remove them |
| Standardize part names | "Compressor", "compressor", "COMPRESSOR", "comp." → all become `compressor` |
| Standardize model names | "RF28X", "RF-28X", "rf-28x" → all become `RF-28X` |
| Validate date ranges | Remove records with impossible dates |
| Anonymize PII | Remove customer names, phone numbers, addresses — keep only region |

### Phase 2: Feature Engineering (Week 2-3)

| Task | Details |
|---|---|
| Calculate asset age | `age = today - installation_date` (older assets have different failure patterns) |
| Create seasonal tags | Tag each complaint with season (summer/monsoon/winter) — AC failures spike in summer |
| Compute part frequency | For each model, calculate how often each part was replaced historically |
| Build error-to-part mapping | From real data, learn which error codes most frequently lead to which parts |
| Generate technician profiles | Calculate each technician's historical accuracy and specialization |

### Phase 3: Build Production Vector Store (Week 3-4)

| Task | Details |
|---|---|
| Convert all historical records to text embeddings | Each record becomes a searchable vector in FAISS |
| Tune chunk size | Experiment with how much text per record gives the best similarity results |
| Build separate indexes per product type | One FAISS index for refrigerators, one for ACs, etc. — improves search precision |
| Benchmark retrieval quality | For 100 known cases, verify that FAISS returns relevant similar cases |

### Phase 4: Prompt Optimization & Testing (Week 4-5)

| Task | Details |
|---|---|
| A/B test different system prompts | Try multiple prompt variations and measure which gives the most accurate part predictions |
| Calibrate confidence thresholds | With real data, the 75%/50% thresholds may need adjustment (maybe 80%/60% works better) |
| Run blind tests | Take 200 real cases, hide the `parts_replaced` field, run through the AI, and compare predictions against actual outcomes |
| Calculate production accuracy | Measure: Precision (how many predicted parts were actually needed), Recall (how many needed parts were predicted) |

### Phase 5: Integration & Deployment (Week 5-7)

| Task | Details |
|---|---|
| Connect to client's CRM/ERP system | Pull live complaint data via API instead of manual input |
| Connect to inventory management system | Real-time stock levels instead of static JSON |
| Set up database | Move from JSON files to a proper database (Firestore, PostgreSQL, etc.) |
| Deploy to cloud | Host on Google Cloud Run or equivalent for team-wide access |
| User training | Train dispatchers and technicians on using the system |

### Phase 6: Continuous Learning Loop (Ongoing)

| Task | Details |
|---|---|
| Collect technician feedback | After every repair, technician confirms if prediction was correct |
| Weekly model retraining | Add new feedback data to the vector store every week |
| Monthly accuracy reports | Track prediction accuracy trend over time |
| Threshold auto-tuning | Automatically adjust confidence thresholds based on accumulated accuracy data |

---

## Section 3: Missing Points You Haven't Considered (And Their Solutions)

### 1. Cold Start Problem
**Problem:** When the client launches a brand new product model (e.g., "RF-50X"), there is zero historical repair data. The AI has nothing to search against.

**Solution:** For new models, fall back to the closest existing model's data (e.g., use RF-28X data for RF-50X since both are refrigerators). As real data accumulates, the system automatically switches to using the new model's own history. Also, proactively load the BOM and known issues from the manufacturer's documentation.

---

### 2. Seasonal & Climate Variation
**Problem:** AC compressors fail far more in May-June (Indian summer) than in December. The AI doesn't currently account for this.

**Solution:** Add a `season` and `region_climate` tag to every historical record. When searching for similar cases, boost the relevance of cases that happened in the same season and similar climate zone.

---

### 3. Data Privacy & Compliance
**Problem:** Customer complaints may contain personal information (names, addresses, phone numbers). Storing and processing this data has legal implications under data protection laws.

**Solution:** Anonymize all PII before the data enters the AI pipeline. Replace customer names with IDs, remove addresses (keep only region/city), and never store raw phone numbers. The AI only needs symptoms, product info, and parts data — not personal details.

---

### 4. Repeat Offender Detection
**Problem:** If the same asset has been serviced 4 times in 6 months for the same symptom, predicting the same part again is clearly wrong. There's a deeper issue (e.g., wiring fault, installation defect).

**Solution:** Before running the normal prediction pipeline, add a **pre-check agent** that looks at the asset's service history. If it detects a repeat pattern, it should automatically escalate to a senior engineer with a flag: "Recurring issue detected — standard part replacement not recommended."

---

### 5. Multi-Language Complaints
**Problem:** If the client operates across India, complaints may come in Hindi, Tamil, Telugu, etc. The current system only works with English text.

**Solution:** Add a translation layer before Agent 1. Google Gemini natively supports multilingual input, so it can extract symptoms from Hindi/Tamil complaints directly. Alternatively, use Google Translate API to convert all complaints to English before processing.

---

### 6. Inventory Sync Lag
**Problem:** If the inventory data is updated only once a day (batch sync), the system might auto-order a part that was already dispatched to another technician an hour ago.

**Solution:** Implement real-time inventory sync via API. If real-time isn't possible, add a "stock buffer" — only auto-order if stock is above a safety threshold (e.g., 3+ units), not just above 0.

---

### 7. Part Combination Patterns
**Problem:** Some failures require replacing multiple parts together (e.g., compressor + refrigerant valve are almost always replaced together). The current system predicts parts independently.

**Solution:** Build a "frequently replaced together" matrix from historical data (similar to Amazon's "customers who bought X also bought Y"). When the AI predicts a compressor, automatically suggest the paired parts as well.

---

### 8. Confidence Calibration Drift
**Problem:** The AI might say "92% confident" but in reality it's only correct 70% of the time. Or the reverse — it says 60% but is actually correct 90% of the time. The confidence scores are not calibrated against real outcomes.

**Solution:** After collecting 500+ feedback responses, run a calibration analysis: plot predicted confidence vs actual accuracy. Use this to build a correction curve. If the AI consistently overestimates confidence by 15%, subtract 15% before applying the ordering threshold.

---

### 9. Warranty-Aware Predictions
**Problem:** If the product is under warranty, the parts should be dispatched for free. If it's out of warranty, the customer should be quoted a cost before ordering. The current system doesn't differentiate.

**Solution:** Add warranty status check to Agent 4. If the asset is under warranty, auto-order freely. If out of warranty, change the workflow to "Generate Quote → Customer Approval → Then Order."

---

### 10. Technician Skill-Based Routing
**Problem:** A junior technician might not be able to replace a compressor (requires gas handling certification). If the AI predicts a compressor replacement, it should ensure the assigned technician is qualified.

**Solution:** Cross-reference the predicted part's complexity level with the assigned technician's skill profile. If there's a mismatch, flag it as: "This repair requires a certified technician — reassign or send a senior alongside."

---

### 11. Photo-Based Diagnosis (Future Enhancement)
**Problem:** Customer complaints in text can be vague ("it's making a weird noise"). A photo or video of the issue would give the AI much more to work with.

**Solution:** Allow customers or field agents to upload photos of the faulty equipment. Use Google Gemini's multimodal capabilities (it can analyze images) to extract visual symptoms (e.g., rust, burn marks, ice buildup, broken fan blades) and feed them into the prediction pipeline alongside the text complaint.

---

### 12. SLA & Priority Routing
**Problem:** Not all customers are equal. A hospital's cold storage failing is far more critical than a home refrigerator. The current system treats all complaints with equal priority.

**Solution:** Add a `customer_tier` field (Platinum/Gold/Silver) and an `asset_criticality` field (Mission-Critical/Standard). Automatically escalate high-tier + high-criticality cases to immediate auto-order regardless of confidence score.

---

## Section 4: Data Request Template for the Client

You can share this exact checklist with the client's data/IT team:

```
DATA REQUEST — AI Parts Recommendation System
==============================================

Please provide the following datasets in CSV or JSON format:

1. [ ] Historical Service Records (minimum 500 records, ideally 2000+)
      Required fields: case_id, complaint_text, product_type, model,
      symptoms, parts_replaced, fix_successful, technician_notes,
      resolution_time, root_cause

2. [ ] Product Master / Asset Catalog
      Required fields: model, product_type, bom_parts,
      common_failure_parts, known_issues, warranty_years

3. [ ] Parts Inventory Snapshot
      Required fields: part_id, part_name, part_description,
      compatible_models, stock_quantity, warehouse_location,
      unit_cost, substitute_part_id

4. [ ] Customer Asset Installation Records
      Required fields: asset_id, customer_id, model, serial_number,
      installation_date, location_region, service_history_count

5. [ ] Error Code Dictionary (if applicable)
      Required fields: error_code, description, applicable_models,
      commonly_associated_parts

6. [ ] Technician Master Data
      Required fields: technician_id, specialization, region,
      skill_level
```

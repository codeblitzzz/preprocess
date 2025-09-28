# RRF Attribute-Contract Matching Report

## Summary
- **Method**: Reciprocal Rank Fusion (Semantic + Keyword)
- **Total Attributes**: 5
- **Total Contract Chunks**: 484
- **Search K**: 50 (results per method before fusion)
- **Final Top K**: 10 (results after RRF)
- **RRF Parameter**: k=60

## RRF Methodology
Reciprocal Rank Fusion combines:
1. **Semantic Similarity**: Vector embeddings with cosine similarity
2. **Keyword Matching**: Exact term matching with frequency scoring
3. **RRF Formula**: Score = Σ(1 / (k + rank)) across both methods

## Attribute Analysis

### 1. Medicaid Timely Filing

**Attribute Content**: Medicaid Timely Filing Submission and Adjudication of Medicaid Claims (Enterprise Agreement) This provision relates to proper claims submission, inclu...

**Keywords Used**: payment, submission, provider, primary payor, secondary payor, claims, agreement, one hundred twenty (120) days, adjudication, coded service identifier

**RRF Statistics**:
- Average RRF Score: 0.028307
- Max RRF Score: 0.032787
- Average Semantic Score: 0.1929

**Top 5 Fused Results**:

1. **Page 48** - RRF Score: 0.032787
   - Section: section:ARTICLE VI > clause:6.1
   - Semantic: Rank #1, Score: 0.744
   - Keyword: Rank #1, Score: 0.4888
   - Content: Submission and Adjudication of Medicare Advantage Claims. Unless otherwise instructed in the provider
manual(s) or Policies applicable to Medicare Advantage Program, or unless required by
Regulatory R...

2. **Page 55** - RRF Score: 0.030777
   - Section: clause:04 > section:ARTICLE II
   - Semantic: Rank #6, Score: 0.1853
   - Keyword: Rank #4, Score: 0.2801
   - Content: Claim with correct code. In addition, Claims with codes which have been deleted will be rejected or denied.
Coding Software. Updates to Claims processing filters, code editing software, pricers, and a...

3. **Page 55** - RRF Score: 0.029643
   - Section: clause:04 > section:ARTICLE II
   - Semantic: Rank #14, Score: 0.1337
   - Keyword: Rank #2, Score: 0.3256
   - Content: Claim Submissions for Pharmaceuticals. Each Claim submitted for a pharmaceutical product must include standard
Coded Service Identifier(s), a National Drug Code ("NDC") number of the covered medicatio...

4. **Page 3** - RRF Score: 0.028958
   - Section: clause:2.5
   - Semantic: Rank #4, Score: 0.1963
   - Keyword: Rank #15, Score: 0.2173
   - Content: Submission and Adjudication of Claims. Provider shall submit, and shall adjudicate, Claims in
accordance with the applicable Participation Attachment(s), the ACS, the provider manual(s) and Regulatory...

5. **Page 4** - RRF Score: 0.028083
   - Section: clause:25
   - Semantic: Rank #7, Score: 0.182
   - Keyword: Rank #16, Score: 0.2161
   - Content: Submission and Adjudication of Claims. Provider shall submit, and a shall adjudicate, Claims in
accordance with the applicable Participation Attachment(s), the ACS, the provider manual(s) and Regulato...

---

### 2. Medicare Timely Filing

**Attribute Content**: Medicare Timely Filing Submission and Adjudication of Medicare Advantage Claims (Enterprise Agreement), Medicare Advantage Attachment, 6.1-6.1.3 This ...

**Keywords Used**: payment, submission, provider, primary payor, ninety (90) day, claims, secondary payor, ninety (90) days, agreement, adjudication

**RRF Statistics**:
- Average RRF Score: 0.028167
- Max RRF Score: 0.032787
- Average Semantic Score: 0.2345

**Top 5 Fused Results**:

1. **Page 48** - RRF Score: 0.032787
   - Section: section:ARTICLE VI > clause:6.1
   - Semantic: Rank #1, Score: 0.8635
   - Keyword: Rank #1, Score: 0.6398
   - Content: Submission and Adjudication of Medicare Advantage Claims. Unless otherwise instructed in the provider
manual(s) or Policies applicable to Medicare Advantage Program, or unless required by
Regulatory R...

2. **Page 55** - RRF Score: 0.029274
   - Section: clause:04 > section:ARTICLE II
   - Semantic: Rank #12, Score: 0.1394
   - Keyword: Rank #5, Score: 0.2801
   - Content: Claim with correct code. In addition, Claims with codes which have been deleted will be rejected or denied.
Coding Software. Updates to Claims processing filters, code editing software, pricers, and a...

3. **Page 55** - RRF Score: 0.028629
   - Section: clause:04 > section:ARTICLE II
   - Semantic: Rank #20, Score: 0.0931
   - Keyword: Rank #2, Score: 0.3256
   - Content: Claim Submissions for Pharmaceuticals. Each Claim submitted for a pharmaceutical product must include standard
Coded Service Identifier(s), a National Drug Code ("NDC") number of the covered medicatio...

4. **Page 3** - RRF Score: 0.028543
   - Section: clause:2.5
   - Semantic: Rank #5, Score: 0.1857
   - Keyword: Rank #16, Score: 0.2173
   - Content: Submission and Adjudication of Claims. Provider shall submit, and shall adjudicate, Claims in
accordance with the applicable Participation Attachment(s), the ACS, the provider manual(s) and Regulatory...

5. **Page 45** - RRF Score: 0.028259
   - Section: section:ARTICLE II > clause:2.1
   - Semantic: Rank #15, Score: 0.103
   - Keyword: Rank #7, Score: 0.2496
   - Content: Participation-Medicare Advantage. As a participant in Medicare Advantage Network, Provider
will render MA Covered Services to MA Members enrolled in Medicare Advantage Program in
accordance with the t...

---

### 3. No Steerage/SOC

**Attribute Content**: No Steerage/SOC Networks and Provider Panels, Base, 2.11 Provision allows Elevance the right to develop designated networks (e.g., high performance ne...

**Keywords Used**: provider, participating provider, agreement, steerage, unless otherwise

**RRF Statistics**:
- Average RRF Score: 0.029393
- Max RRF Score: 0.032018
- Average Semantic Score: 0.1424

**Top 5 Fused Results**:

1. **Page 12** - RRF Score: 0.032018
   - Section: clause:7
   - Semantic: Rank #4, Score: 0.2336
   - Keyword: Rank #1, Score: 0.5854
   - Content: The terms and conditions of Provider's participation as a Participating Provider in such
additional Networks, products and/or programs shall be on the terms and conditions as set forth in this
Agreeme...

2. **Page 11** - RRF Score: 0.031754
   - Section: clause:8.5 > section:ARTICLE VIII
   - Semantic: Rank #2, Score: 0.2837
   - Keyword: Rank #4, Score: 0.469
   - Content: connection with Provider and/or any and all Participating Providers as to which the Agreement has not been
terminated. Notwithstanding the foregoing, reserves the right to terminate Participating
Prov...

3. **Page 22** - RRF Score: 0.031258
   - Section: clause:8.5 > section:Section VII - Regulatory Requirements
   - Semantic: Rank #3, Score: 0.2676
   - Keyword: Rank #5, Score: 0.468
   - Content: connection with Provider and/or any and all Participating Providers as to which the Agreement has not been
terminated. Notwithstanding the foregoing, — reserves the right to terminate Participating
Pr...

4. **Page 2** - RRF Score: 0.031025
   - Section: clause:7
   - Semantic: Rank #6, Score: 0.1497
   - Keyword: Rank #3, Score: 0.5767
   - Content: that is to an agreement to provide Covered Services to Members that has met all applicable required
RENE = 2ertng requirements and accreditation requirements for the services the Participating Provide...

5. **Page 2** - RRF Score: 0.02895
   - Section: clause:7
   - Semantic: Rank #18, Score: 0.0498
   - Keyword: Rank #2, Score: 0.579
   - Content: Attachment(s).
"Member" means any individual who is eligible, as determined by — as applicable, and Lami to
receive Covered Services under a Health Benefit Plan. For all purposes related to this Agree...

---

### 4. Medicaid Fee Schedule

**Attribute Content**: Medicaid Fee Schedule Plan Compensation Schedule (Attachement) - Under Article called "Specific Reimbursement Terms" Specifies the methodology for cal...

**Keywords Used**: one hundred percent, provider, agreement, specific reimbursement terms, compensation, covered services, reimbursement, rate, fee schedule, medicaid

**RRF Statistics**:
- Average RRF Score: 0.029178
- Max RRF Score: 0.031514
- Average Semantic Score: 0.2041

**Top 5 Fused Results**:

1. **Page 60** - RRF Score: 0.031514
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #2, Score: 0.3612
   - Keyword: Rank #5, Score: 0.3833
   - Content: Specialty Provider Individual and/or group (Non-MD or DO) shall be reimbursed in accordance with Regulatory
Requirements for the applicable methodology based on the referenced fee schedule. If such re...

2. **Page 60** - RRF Score: 0.030536
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #5, Score: 0.1739
   - Keyword: Rank #6, Score: 0.3753
   - Content: basis for facilitation of collaborative programs meant to manage medical/social/mental health conditions more
effectively.
"Medicare Fee Schedule" means the applicable Medicare Fee Schedule for the pr...

3. **Page 61** - RRF Score: 0.029907
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #1, Score: 0.4732
   - Keyword: Rank #14, Score: 0.355
   - Content: "Tennessee Medicaid Rate(s)/Fee Schedule(s)/Methodologies" means the Tennessee Medicaid Rate(s)/Fee
Schedule(s)/ in effect on the date of service for the provider type(s)/service(s) identified herein ...

4. **Page 56** - RRF Score: 0.029828
   - Section: clause:04 > section:ARTICLE II
   - Semantic: Rank #13, Score: 0.069
   - Keyword: Rank #2, Score: 0.4424
   - Content: billing, collecting or attempting to collect from or Members. Notwithstanding the foregoing, if
has a direct contract with the subcontractor, the direct contract shall prevail over this Agreement and ...

5. **Page 60** - RRF Score: 0.02886
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #3, Score: 0.3123
   - Keyword: Rank #17, Score: 0.3159
   - Content: Agreement. DMEPOS and PEN Fee Schedule and/or rate changes will be applied on a prospective
basis.
" Professional Provider Market Master Fee Schedule(s)/Rate(s)/Methodologies " means the proprietary
r...

---

### 5. Medicare Fee Schedule

**Attribute Content**: Medicare Fee Schedule Plan Compensation Schedule (Attachement) - Under Article called "Specific Reimbursement Terms" Specifies the methodology for cal...

**Keywords Used**: payment, provider, agreement, specific reimbursement terms, compensation, covered services, reimbursement, rate, network, fee schedule

**RRF Statistics**:
- Average RRF Score: 0.029102
- Max RRF Score: 0.032266
- Average Semantic Score: 0.208

**Top 5 Fused Results**:

1. **Page 45** - RRF Score: 0.032266
   - Section: section:ARTICLE II > clause:2.1
   - Semantic: Rank #1, Score: 0.3744
   - Keyword: Rank #3, Score: 0.4474
   - Content: Participation-Medicare Advantage. As a participant in Medicare Advantage Network, Provider
will render MA Covered Services to MA Members enrolled in Medicare Advantage Program in
accordance with the t...

2. **Page 60** - RRF Score: 0.032002
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #3, Score: 0.27
   - Keyword: Rank #2, Score: 0.451
   - Content: basis for facilitation of collaborative programs meant to manage medical/social/mental health conditions more
effectively.
"Medicare Fee Schedule" means the applicable Medicare Fee Schedule for the pr...

3. **Page 60** - RRF Score: 0.030777
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #6, Score: 0.1989
   - Keyword: Rank #4, Score: 0.4458
   - Content: Specialty Provider Individual and/or group (Non-MD or DO) shall be reimbursed in accordance with Regulatory
Requirements for the applicable methodology based on the referenced fee schedule. If such re...

4. **Page 1** - RRF Score: 0.029907
   - Section: clause:7
   - Semantic: Rank #14, Score: 0.1185
   - Keyword: Rank #1, Score: 0.4983
   - Content: Compensation Schedule" ("ACS") means the document(s) attached hereto and incorporated herein by
reference, and which sets forth ‘he Rate(s) and compensation related terms for the Network(s) in which
P...

5. **Page 60** - RRF Score: 0.029644
   - Section: clause:2.2.3 > section:ARTICLE I
   - Semantic: Rank #9, Score: 0.1529
   - Keyword: Rank #6, Score: 0.3974
   - Content: Agreement. DMEPOS and PEN Fee Schedule and/or rate changes will be applied on a prospective
basis.
" Professional Provider Market Master Fee Schedule(s)/Rate(s)/Methodologies " means the proprietary
r...

---


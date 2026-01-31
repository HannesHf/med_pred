# MIMIC-IV Tabellen Übersicht

Erstellt für Pfad: `../../data/mimic-iv-3.1/`

### 📂 Tabelle: `caregiver` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\caregiver.csv.gz`
- **Spalten:** `caregiver_id`

**Beispielzeile:**
|   caregiver_id |
|---------------:|
|              3 |

---

### 📂 Tabelle: `chartevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\chartevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `charttime`, `storetime`, `itemid`, `value`, `valuenum`, `valueuom`, `warning`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | charttime           | storetime           |   itemid |   value |   valuenum | valueuom   |   warning |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|---------:|--------:|-----------:|:-----------|----------:|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 12:36:00 | 2180-07-23 14:45:00 |   226512 |    39.4 |       39.4 | kg         |         0 |

---

### 📂 Tabelle: `datetimeevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\datetimeevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `charttime`, `storetime`, `itemid`, `value`, `valueuom`, `warning`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | charttime           | storetime           |   itemid | value               | valueuom   |   warning |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|---------:|:--------------------|:-----------|----------:|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 14:24:00 | 2180-07-23 14:24:00 |   225754 | 2180-07-23 14:24:00 | Date       |         0 |

---

### 📂 Tabelle: `d_items` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\d_items.csv.gz`
- **Spalten:** `itemid`, `label`, `abbreviation`, `linksto`, `category`, `unitname`, `param_type`, `lownormalvalue`, `highnormalvalue`

**Beispielzeile:**
|   itemid | label        | abbreviation   | linksto     | category   |   unitname | param_type   |   lownormalvalue |   highnormalvalue |
|---------:|:-------------|:---------------|:------------|:-----------|-----------:|:-------------|-----------------:|------------------:|
|   220001 | Problem List | Problem List   | chartevents | General    |        nan | Text         |              nan |               nan |

---

### 📂 Tabelle: `icustays` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\icustays.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `first_careunit`, `last_careunit`, `intime`, `outtime`, `los`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id | first_careunit                     | last_careunit                      | intime              | outtime             |      los |
|-------------:|----------:|----------:|:-----------------------------------|:-----------------------------------|:--------------------|:--------------------|---------:|
|     10000032 |  29079034 |  39553978 | Medical Intensive Care Unit (MICU) | Medical Intensive Care Unit (MICU) | 2180-07-23 14:00:00 | 2180-07-23 23:50:47 | 0.410266 |

---

### 📂 Tabelle: `ingredientevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\ingredientevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `starttime`, `endtime`, `storetime`, `itemid`, `amount`, `amountuom`, `rate`, `rateuom`, `orderid`, `linkorderid`, `statusdescription`, `originalamount`, `originalrate`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | starttime           | endtime             | storetime           |   itemid |   amount | amountuom   |   rate |   rateuom |   orderid |   linkorderid | statusdescription   |   originalamount |   originalrate |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|:--------------------|---------:|---------:|:------------|-------:|----------:|----------:|--------------:|:--------------------|-----------------:|---------------:|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 17:00:00 | 2180-07-23 17:01:00 | 2180-07-23 18:56:00 |   220490 |      200 | mL          |    nan |       nan |   3782233 |       3782233 | FinishedRunning     |                0 |            200 |

---

### 📂 Tabelle: `inputevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\inputevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `starttime`, `endtime`, `storetime`, `itemid`, `amount`, `amountuom`, `rate`, `rateuom`, `orderid`, `linkorderid`, `ordercategoryname`, `secondaryordercategoryname`, `ordercomponenttypedescription`, `ordercategorydescription`, `patientweight`, `totalamount`, `totalamountuom`, `isopenbag`, `continueinnextdept`, `statusdescription`, `originalamount`, `originalrate`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | starttime           | endtime             | storetime           |   itemid |   amount | amountuom   |   rate |   rateuom |   orderid |   linkorderid | ordercategoryname      |   secondaryordercategoryname | ordercomponenttypedescription   | ordercategorydescription   |   patientweight |   totalamount | totalamountuom   |   isopenbag |   continueinnextdept | statusdescription   |   originalamount |   originalrate |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|:--------------------|---------:|---------:|:------------|-------:|----------:|----------:|--------------:|:-----------------------|-----------------------------:|:--------------------------------|:---------------------------|----------------:|--------------:|:-----------------|------------:|---------------------:|:--------------------|-----------------:|---------------:|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 17:00:00 | 2180-07-23 17:01:00 | 2180-07-23 18:56:00 |   226452 |      200 | mL          |    nan |       nan |   3782233 |       3782233 | 14-Oral/Gastric Intake |                          nan | Main order parameter            | Bolus                      |            39.4 |           200 | mL               |           0 |                    0 | FinishedRunning     |              200 |            200 |

---

### 📂 Tabelle: `outputevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\outputevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `charttime`, `storetime`, `itemid`, `value`, `valueuom`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | charttime           | storetime           |   itemid |   value | valueuom   |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|---------:|--------:|:-----------|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 15:00:00 | 2180-07-23 16:00:00 |   226560 |     175 | mL         |

---

### 📂 Tabelle: `procedureevents` (aus `icu`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/icu\procedureevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `stay_id`, `caregiver_id`, `starttime`, `endtime`, `storetime`, `itemid`, `value`, `valueuom`, `location`, `locationcategory`, `orderid`, `linkorderid`, `ordercategoryname`, `ordercategorydescription`, `patientweight`, `isopenbag`, `continueinnextdept`, `statusdescription`, `originalamount`, `originalrate`

**Beispielzeile:**
|   subject_id |   hadm_id |   stay_id |   caregiver_id | starttime           | endtime             | storetime           |   itemid |   value |   valueuom |   location |   locationcategory |   orderid |   linkorderid | ordercategoryname   | ordercategorydescription   |   patientweight |   isopenbag |   continueinnextdept | statusdescription   |   originalamount |   originalrate |
|-------------:|----------:|----------:|---------------:|:--------------------|:--------------------|:--------------------|---------:|--------:|-----------:|-----------:|-------------------:|----------:|--------------:|:--------------------|:---------------------------|----------------:|------------:|---------------------:|:--------------------|-----------------:|---------------:|
|     10000032 |  29079034 |  39553978 |          18704 | 2180-07-23 14:43:00 | 2180-07-23 14:44:00 | 2180-07-23 14:43:00 |   225966 |       1 |        nan |        nan |                nan |   3050203 |       3050203 | Procedures          | Task                       |            39.4 |           0 |                    0 | FinishedRunning     |                1 |              0 |

---

### 📂 Tabelle: `admissions` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\admissions.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `admittime`, `dischtime`, `deathtime`, `admission_type`, `admit_provider_id`, `admission_location`, `discharge_location`, `insurance`, `language`, `marital_status`, `race`, `edregtime`, `edouttime`, `hospital_expire_flag`

**Beispielzeile:**
|   subject_id |   hadm_id | admittime           | dischtime           |   deathtime | admission_type   | admit_provider_id   | admission_location     | discharge_location   | insurance   | language   | marital_status   | race   | edregtime           | edouttime           |   hospital_expire_flag |
|-------------:|----------:|:--------------------|:--------------------|------------:|:-----------------|:--------------------|:-----------------------|:---------------------|:------------|:-----------|:-----------------|:-------|:--------------------|:--------------------|-----------------------:|
|     10000032 |  22595853 | 2180-05-06 22:23:00 | 2180-05-07 17:15:00 |         nan | URGENT           | P49AFC              | TRANSFER FROM HOSPITAL | HOME                 | Medicaid    | English    | WIDOWED          | WHITE  | 2180-05-06 19:17:00 | 2180-05-06 23:30:00 |                      0 |

---

### 📂 Tabelle: `diagnoses_icd` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\diagnoses_icd.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `seq_num`, `icd_code`, `icd_version`

**Beispielzeile:**
|   subject_id |     hadm_id |   seq_num |   icd_code |   icd_version |
|-------------:|------------:|----------:|-----------:|--------------:|
|        1e+07 | 2.25959e+07 |         1 |       5723 |             9 |

---

### 📂 Tabelle: `drgcodes` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\drgcodes.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `drg_type`, `drg_code`, `description`, `drg_severity`, `drg_mortality`

**Beispielzeile:**
|   subject_id |   hadm_id | drg_type   |   drg_code | description                  |   drg_severity |   drg_mortality |
|-------------:|----------:|:-----------|-----------:|:-----------------------------|---------------:|----------------:|
|     10000032 |  22595853 | APR        |        283 | OTHER DISORDERS OF THE LIVER |              2 |               2 |

---

### 📂 Tabelle: `d_hcpcs` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\d_hcpcs.csv.gz`
- **Spalten:** `code`, `category`, `long_description`, `short_description`

**Beispielzeile:**
|   code |   category |   long_description | short_description   |
|-------:|-----------:|-------------------:|:--------------------|
|      0 |        nan |                nan | Invalid Code        |

---

### 📂 Tabelle: `d_icd_diagnoses` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\d_icd_diagnoses.csv.gz`
- **Spalten:** `icd_code`, `icd_version`, `long_title`

**Beispielzeile:**
|   icd_code |   icd_version | long_title                     |
|-----------:|--------------:|:-------------------------------|
|         10 |             9 | Cholera due to vibrio cholerae |

---

### 📂 Tabelle: `d_icd_procedures` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\d_icd_procedures.csv.gz`
- **Spalten:** `icd_code`, `icd_version`, `long_title`

**Beispielzeile:**
|   icd_code |   icd_version | long_title                                         |
|-----------:|--------------:|:---------------------------------------------------|
|          1 |             9 | Therapeutic ultrasound of vessels of head and neck |

---

### 📂 Tabelle: `d_labitems` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\d_labitems.csv.gz`
- **Spalten:** `itemid`, `label`, `fluid`, `category`

**Beispielzeile:**
|   itemid | label                      | fluid   | category   |
|---------:|:---------------------------|:--------|:-----------|
|    50801 | Alveolar-arterial Gradient | Blood   | Blood Gas  |

---

### 📂 Tabelle: `emar` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\emar.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `emar_id`, `emar_seq`, `poe_id`, `pharmacy_id`, `enter_provider_id`, `charttime`, `medication`, `event_txt`, `scheduletime`, `storetime`

**Beispielzeile:**
|   subject_id |   hadm_id | emar_id     |   emar_seq | poe_id      |   pharmacy_id |   enter_provider_id | charttime           | medication   | event_txt    | scheduletime        | storetime           |
|-------------:|----------:|:------------|-----------:|:------------|--------------:|--------------------:|:--------------------|:-------------|:-------------|:--------------------|:--------------------|
|     10000032 |  22595853 | 10000032-10 |         10 | 10000032-32 |      86768272 |                 nan | 2180-05-07 07:51:00 | Heparin      | Administered | 2180-05-07 08:00:00 | 2180-05-07 07:56:00 |

---

### 📂 Tabelle: `emar_detail` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\emar_detail.csv.gz`
- **Spalten:** `subject_id`, `emar_id`, `emar_seq`, `parent_field_ordinal`, `administration_type`, `pharmacy_id`, `barcode_type`, `reason_for_no_barcode`, `complete_dose_not_given`, `dose_due`, `dose_due_unit`, `dose_given`, `dose_given_unit`, `will_remainder_of_dose_be_given`, `product_amount_given`, `product_unit`, `product_code`, `product_description`, `product_description_other`, `prior_infusion_rate`, `infusion_rate`, `infusion_rate_adjustment`, `infusion_rate_adjustment_amount`, `infusion_rate_unit`, `route`, `infusion_complete`, `completion_interval`, `new_iv_bag_hung`, `continued_infusion_in_other_location`, `restart_interval`, `side`, `site`, `non_formulary_visual_verification`

**Beispielzeile:**
|   subject_id | emar_id     |   emar_seq |   parent_field_ordinal |   administration_type |   pharmacy_id | barcode_type   |   reason_for_no_barcode |   complete_dose_not_given |   dose_due |   dose_due_unit |   dose_given | dose_given_unit   |   will_remainder_of_dose_be_given |   product_amount_given | product_unit   | product_code   | product_description                      |   product_description_other |   prior_infusion_rate |   infusion_rate |   infusion_rate_adjustment |   infusion_rate_adjustment_amount |   infusion_rate_unit |   route |   infusion_complete |   completion_interval |   new_iv_bag_hung |   continued_infusion_in_other_location |   restart_interval |   side |   site |   non_formulary_visual_verification |
|-------------:|:------------|-----------:|-----------------------:|----------------------:|--------------:|:---------------|------------------------:|--------------------------:|-----------:|----------------:|-------------:|:------------------|----------------------------------:|-----------------------:|:---------------|:---------------|:-----------------------------------------|----------------------------:|----------------------:|----------------:|---------------------------:|----------------------------------:|---------------------:|--------:|--------------------:|----------------------:|------------------:|---------------------------------------:|-------------------:|-------:|-------:|------------------------------------:|
|     10000032 | 10000032-10 |         10 |                    1.1 |                   nan |      86768272 | if             |                     nan |                       nan |        nan |             nan |         5000 | UNIT              |                               nan |                      1 | mL             | HEPA5I         | Heparin Sodium 5000 Units / mL- 1mL Vial |                         nan |                   nan |             nan |                        nan |                               nan |                  nan |     nan |                 nan |                   nan |               nan |                                    nan |                nan |    nan |    nan |                                 nan |

---

### 📂 Tabelle: `hcpcsevents` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\hcpcsevents.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `chartdate`, `hcpcs_cd`, `seq_num`, `short_description`

**Beispielzeile:**
|   subject_id |   hadm_id | chartdate   |   hcpcs_cd |   seq_num | short_description             |
|-------------:|----------:|:------------|-----------:|----------:|:------------------------------|
|     10000068 |  25022803 | 2160-03-04  |      99218 |         1 | Hospital observation services |

---

### 📂 Tabelle: `labevents` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\labevents.csv.gz`
- **Spalten:** `labevent_id`, `subject_id`, `hadm_id`, `specimen_id`, `itemid`, `order_provider_id`, `charttime`, `storetime`, `value`, `valuenum`, `valueuom`, `ref_range_lower`, `ref_range_upper`, `flag`, `priority`, `comments`

**Beispielzeile:**
|   labevent_id |   subject_id |   hadm_id |   specimen_id |   itemid | order_provider_id   | charttime           | storetime           | value   |   valuenum | valueuom   |   ref_range_lower |   ref_range_upper |   flag | priority   | comments                                              |
|--------------:|-------------:|----------:|--------------:|---------:|:--------------------|:--------------------|:--------------------|:--------|-----------:|:-----------|------------------:|------------------:|-------:|:-----------|:------------------------------------------------------|
|             1 |     10000032 |       nan |       2704548 |    50931 | P69FQC              | 2180-03-23 11:51:00 | 2180-03-23 15:56:00 | ___     |         95 | mg/dL      |                70 |               100 |    nan | ROUTINE    | IF FASTING, 70-100 NORMAL, >125 PROVISIONAL DIABETES. |

---

### 📂 Tabelle: `microbiologyevents` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\microbiologyevents.csv.gz`
- **Spalten:** `microevent_id`, `subject_id`, `hadm_id`, `micro_specimen_id`, `order_provider_id`, `chartdate`, `charttime`, `spec_itemid`, `spec_type_desc`, `test_seq`, `storedate`, `storetime`, `test_itemid`, `test_name`, `org_itemid`, `org_name`, `isolate_num`, `quantity`, `ab_itemid`, `ab_name`, `dilution_text`, `dilution_comparison`, `dilution_value`, `interpretation`, `comments`

**Beispielzeile:**
|   microevent_id |   subject_id |   hadm_id |   micro_specimen_id | order_provider_id   | chartdate           | charttime           |   spec_itemid | spec_type_desc   |   test_seq | storedate           | storetime           |   test_itemid | test_name      |   org_itemid |   org_name |   isolate_num |   quantity |   ab_itemid |   ab_name |   dilution_text |   dilution_comparison |   dilution_value |   interpretation | comments   |
|----------------:|-------------:|----------:|--------------------:|:--------------------|:--------------------|:--------------------|--------------:|:-----------------|-----------:|:--------------------|:--------------------|--------------:|:---------------|-------------:|-----------:|--------------:|-----------:|------------:|----------:|----------------:|----------------------:|-----------------:|-----------------:|:-----------|
|               1 |     10000032 |       nan |             1304715 | P69FQC              | 2180-03-23 00:00:00 | 2180-03-23 11:51:00 |         70046 | IMMUNOLOGY       |          1 | 2180-03-26 00:00:00 | 2180-03-26 10:54:00 |         90123 | HCV VIRAL LOAD |          nan |        nan |           nan |        nan |         nan |       nan |             nan |                   nan |              nan |              nan | ___        |

---

### 📂 Tabelle: `omr` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\omr.csv.gz`
- **Spalten:** `subject_id`, `chartdate`, `seq_num`, `result_name`, `result_value`

**Beispielzeile:**
|   subject_id | chartdate   |   seq_num | result_name    | result_value   |
|-------------:|:------------|----------:|:---------------|:---------------|
|     10000032 | 2180-04-27  |         1 | Blood Pressure | 110/65         |

---

### 📂 Tabelle: `patients` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\patients.csv.gz`
- **Spalten:** `subject_id`, `gender`, `anchor_age`, `anchor_year`, `anchor_year_group`, `dod`

**Beispielzeile:**
|   subject_id | gender   |   anchor_age |   anchor_year | anchor_year_group   | dod        |
|-------------:|:---------|-------------:|--------------:|:--------------------|:-----------|
|     10000032 | F        |           52 |          2180 | 2014 - 2016         | 2180-09-09 |

---

### 📂 Tabelle: `pharmacy` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\pharmacy.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `pharmacy_id`, `poe_id`, `starttime`, `stoptime`, `medication`, `proc_type`, `status`, `entertime`, `verifiedtime`, `route`, `frequency`, `disp_sched`, `infusion_type`, `sliding_scale`, `lockout_interval`, `basal_rate`, `one_hr_max`, `doses_per_24_hrs`, `duration`, `duration_interval`, `expiration_value`, `expiration_unit`, `expirationdate`, `dispensation`, `fill_quantity`

**Beispielzeile:**
|   subject_id |   hadm_id |   pharmacy_id | poe_id      | starttime           | stoptime            | medication   | proc_type   | status                             | entertime           | verifiedtime        | route   | frequency   |   disp_sched |   infusion_type |   sliding_scale |   lockout_interval |   basal_rate |   one_hr_max |   doses_per_24_hrs |   duration | duration_interval   |   expiration_value | expiration_unit   |   expirationdate | dispensation   |   fill_quantity |
|-------------:|----------:|--------------:|:------------|:--------------------|:--------------------|:-------------|:------------|:-----------------------------------|:--------------------|:--------------------|:--------|:------------|-------------:|----------------:|----------------:|-------------------:|-------------:|-------------:|-------------------:|-----------:|:--------------------|-------------------:|:------------------|-----------------:|:---------------|----------------:|
|     10000032 |  22595853 |      12775705 | 10000032-55 | 2180-05-08 08:00:00 | 2180-05-07 22:00:00 | Furosemide   | Unit Dose   | Discontinued via patient discharge | 2180-05-07 09:32:35 | 2180-05-07 09:32:35 | PO/NG   | DAILY       |            8 |             nan |             nan |                nan |          nan |          nan |                  1 |        nan | Ongoing             |                 36 | Hours             |              nan | Omnicell       |             nan |

---

### 📂 Tabelle: `poe` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\poe.csv.gz`
- **Spalten:** `poe_id`, `poe_seq`, `subject_id`, `hadm_id`, `ordertime`, `order_type`, `order_subtype`, `transaction_type`, `discontinue_of_poe_id`, `discontinued_by_poe_id`, `order_provider_id`, `order_status`

**Beispielzeile:**
| poe_id       |   poe_seq |   subject_id |   hadm_id | ordertime           | order_type   |   order_subtype | transaction_type   |   discontinue_of_poe_id |   discontinued_by_poe_id | order_provider_id   | order_status   |
|:-------------|----------:|-------------:|----------:|:--------------------|:-------------|----------------:|:-------------------|------------------------:|-------------------------:|:--------------------|:---------------|
| 10000032-100 |       100 |     10000032 |  22841357 | 2180-06-26 22:09:02 | Medications  |             nan | New                |                     nan |                      nan | P992IN              | Inactive       |

---

### 📂 Tabelle: `poe_detail` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\poe_detail.csv.gz`
- **Spalten:** `poe_id`, `poe_seq`, `subject_id`, `field_name`, `field_value`

**Beispielzeile:**
| poe_id       |   poe_seq |   subject_id | field_name   | field_value             |
|:-------------|----------:|-------------:|:-------------|:------------------------|
| 10000032-101 |       101 |     10000032 | Code status  | Resuscitate (Full code) |

---

### 📂 Tabelle: `prescriptions` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\prescriptions.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `pharmacy_id`, `poe_id`, `poe_seq`, `order_provider_id`, `starttime`, `stoptime`, `drug_type`, `drug`, `formulary_drug_cd`, `gsn`, `ndc`, `prod_strength`, `form_rx`, `dose_val_rx`, `dose_unit_rx`, `form_val_disp`, `form_unit_disp`, `doses_per_24_hrs`, `route`

**Beispielzeile:**
|   subject_id |   hadm_id |   pharmacy_id | poe_id      |   poe_seq | order_provider_id   | starttime           | stoptime            | drug_type   | drug       | formulary_drug_cd   |   gsn |         ndc | prod_strength   |   form_rx |   dose_val_rx | dose_unit_rx   |   form_val_disp | form_unit_disp   |   doses_per_24_hrs | route   |
|-------------:|----------:|--------------:|:------------|----------:|:--------------------|:--------------------|:--------------------|:------------|:-----------|:--------------------|------:|------------:|:----------------|----------:|--------------:|:---------------|----------------:|:-----------------|-------------------:|:--------|
|     10000032 |  22595853 |      12775705 | 10000032-55 |        55 | P85UQ1              | 2180-05-08 08:00:00 | 2180-05-07 22:00:00 | MAIN        | Furosemide | FURO40              |  8209 | 51079007320 | 40mg Tablet     |       nan |            40 | mg             |               1 | TAB              |                  1 | PO/NG   |

---

### 📂 Tabelle: `procedures_icd` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\procedures_icd.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `seq_num`, `chartdate`, `icd_code`, `icd_version`

**Beispielzeile:**
|   subject_id |   hadm_id |   seq_num | chartdate   |   icd_code |   icd_version |
|-------------:|----------:|----------:|:------------|-----------:|--------------:|
|     10000032 |  22595853 |         1 | 2180-05-07  |       5491 |             9 |

---

### 📂 Tabelle: `provider` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\provider.csv.gz`
- **Spalten:** `provider_id`

**Beispielzeile:**
| provider_id   |
|:--------------|
| P00019        |

---

### 📂 Tabelle: `services` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\services.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `transfertime`, `prev_service`, `curr_service`

**Beispielzeile:**
|   subject_id |   hadm_id | transfertime        |   prev_service | curr_service   |
|-------------:|----------:|:--------------------|---------------:|:---------------|
|     10000032 |  22595853 | 2180-05-06 22:24:57 |            nan | MED            |

---

### 📂 Tabelle: `transfers` (aus `hosp`)
- **Voller Pfad:** `../../data/mimic-iv-3.1/hosp\transfers.csv.gz`
- **Spalten:** `subject_id`, `hadm_id`, `transfer_id`, `eventtype`, `careunit`, `intime`, `outtime`

**Beispielzeile:**
|   subject_id |   hadm_id |   transfer_id | eventtype   | careunit             | intime              | outtime             |
|-------------:|----------:|--------------:|:------------|:---------------------|:--------------------|:--------------------|
|     10000032 |  22595853 |      33258284 | ED          | Emergency Department | 2180-05-06 19:17:00 | 2180-05-06 23:30:00 |

---


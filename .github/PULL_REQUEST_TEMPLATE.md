## Gate / البوابة
- Gate: (e.g., CALL-1)  
  البوابة: (مثال: CALL-1)
- Gate file: /gates/<GATE>.md  
  ملف البوابة: /gates/<GATE>.md
- Related issue: #<ID>  
  التذكرة المرتبطة: #<ID>

---

## Risk Level / مستوى المخاطر
> Select one: L0 / L1 / L2 / L3 (see /ops/HITL_POLICY.md)  
> اختر واحد: L0 / L1 / L2 / L3 (انظر /ops/HITL_POLICY.md)

- **Risk Level:** L_ (Safe/Normal/Sensitive/Critical)  
  **مستوى المخاطر:** L_ (آمن/عادي/حساس/حرج)

| Level | Description | Approval |
|-------|-------------|----------|
| L0 | Docs, formatting, comments | Auto-merge OK |
| L1 | Code with tests passing | 1 human |
| L2 | Auth, payments, data, secrets | 2 humans |
| L3 | Money, production, irreversible | CEO Gate approval |

---

## Summary / ملخص
- What changed (2–5 bullets)  
  ما الذي تغيّر (2–5 نقاط)

---

## What Could Go Wrong? / ما الذي يمكن أن يحدث خطأ؟
> Describe potential risks of this change  
> صف المخاطر المحتملة لهذا التغيير

- Risk:  
  خطر:
- Mitigation:  
  حل:

---

## Acceptance Criteria Checklist / قائمة شروط النجاح (Pass/Fail)
> Copy from the gate file and check them off  
> انسخ الشروط من ملف البوابة وضع علامة ✓

- [ ] AC1:  
  شرط 1:
- [ ] AC2:  
  شرط 2:
- [ ] AC3:  
  شرط 3:

---

## Evidence (Required) / الدليل (إلزامي)
> Proof beats summaries. Add real outputs.  
> الدليل أهم من الكلام. ضع مخرجات حقيقية.

- [ ] Test/log output (paste or link):  
  نتائج الاختبار/السجلات (الصقها أو ضع رابط):
- [ ] Repro steps (exact steps):  
  خطوات إعادة التجربة (خطوات دقيقة):
- [ ] Demo runbook / recording (if relevant):  
  خطة العرض/تسجيل (إن وجد):
- [ ] Screenshots (if UI):  
  صور شاشة (إن كانت واجهة):

---

## Files touched / الملفات التي تم تعديلها
- [ ] /ops/STATE.md updated (required if gate or status changed)  
  تم تحديث /ops/STATE.md (إلزامي إذا تغيّرت البوابة أو الحالة)
- [ ] /ops/EVIDENCE.md updated (recommended)  
  تم تحديث /ops/EVIDENCE.md (مستحسن)

---

## HITL Checklist / قائمة التحقق البشري
> For L2/L3 changes, both boxes must be checked by different humans  
> للتغييرات L2/L3، يجب أن يتحقق شخصان مختلفان

- [ ] **CEO Review:** I have reviewed scope and intent  
  **مراجعة المدير:** راجعت النطاق والهدف
- [ ] **QA Review:** I have verified evidence and tested  
  **مراجعة الجودة:** تحققت من الدليل واختبرت

---

## Rollback Plan / خطة الرجوع
> If this breaks, how do we revert safely?  
> إذا حدثت مشكلة، كيف نرجع بأمان؟

- Rollback steps:  
  خطوات الرجوع:

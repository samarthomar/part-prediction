# Demo Preparation Guide — Your First Demo

---

## Part 1: Pre-Demo Checklist (Do This 30 Minutes Before the Call)

### Technical Setup

- [ ] **Close all unnecessary apps** — Only VS Code and one Chrome tab should be open
- [ ] **Run the app once and test it BEFORE the call** — Run a complaint end-to-end and make sure all 5 agents complete without errors
- [ ] **Clear old data** — Delete all records from the dashboard so it looks clean for the demo
- [ ] **Keep the terminal visible but small** — The audience will see the agent logs scrolling in real-time (this looks impressive)
- [ ] **Zoom in your browser to 110-125%** — So text is easily readable on screen share
- [ ] **Use a simple, short complaint for the demo** — Don't use a paragraph. Use something crisp like the one below
- [ ] **Turn off all notifications** — Slack, Teams, WhatsApp, Email — EVERYTHING. One popup during demo = embarrassment
- [ ] **Have a backup complaint ready** — If the first one fails (API error), immediately switch to a second one without panicking
- [ ] **Keep the PPT open in a separate window** — In case they ask for an architecture overview, you can quickly switch

### Your Screen Layout
```
Left side:  VS Code terminal (showing agent execution logs)
Right side: Chrome browser (Streamlit app full screen)
```

---

## Part 2: The Demo Script (15 Minutes Total)

### Opening — Set the Stage (2 minutes)

> **What to say:**
>
> "Thank you for joining today. I want to walk you through a working prototype we've built for predictive parts recommendation. Before I show you the tool, let me quickly set the context."
>
> "In traditional field service operations, when a customer raises a complaint, a technician visits the site, diagnoses the issue, then goes back to order parts, waits for delivery, and returns again to fix it. This double-trip costs time, money, and customer satisfaction."
>
> "What if, the moment a complaint is registered, an AI system could automatically predict which parts will be needed, check warehouse stock, and initiate the order — all before the technician even leaves for the site?"
>
> "That's exactly what this prototype does. Let me show you."

**Tip:** Don't rush this. Speak slowly. Let them feel the problem before you show the solution.

---

### Live Demo — The Wow Moment (8 minutes)

**Step 1: Show the Landing Page (30 seconds)**

> "This is the main interface. On the left sidebar, we input the customer complaint. On the right, you can see the 5 AI agents that will process this complaint in sequence."

**Step 2: Enter a Complaint (30 seconds)**

Use this exact complaint (it's short, clear, and produces great results):

```
My refrigerator is not cooling at all. There is heavy ice buildup on the back panel 
and it makes a loud humming noise continuously. The model is RF-28X, approximately 
5 years old.
```

> "I'm entering a real-world type complaint here — a customer saying their refrigerator isn't cooling, there's ice buildup, and a humming noise. Let me also select the product type as Refrigerator and model as RF-28X."

**Step 3: Click "Run AI Recommendation" (30 seconds)**

> "Now I'll click Run, and watch the 5 agents execute one by one in real-time."

**PAUSE HERE. Let the agents run. Don't talk while they're executing.** The audience will watch the boxes turn green one by one — this is visually impressive and builds anticipation. Just let it breathe for 10-15 seconds.

**Step 4: Walk Through Results — Agent 1 (1 minute)**

> "Agent 1 has read the raw complaint and extracted structured data. It identified this as a Refrigerator, model RF-28X, with three symptoms: not cooling, ice buildup, and humming noise. It also assessed the urgency as Medium."
>
> "This is important because in the current process, a call center agent would have to manually log all this — often with errors. Here, the AI does it instantly and accurately."

**Step 5: Walk Through Results — Agent 2 (1 minute)**

> "Agent 2 searched our historical repair database using vector similarity search — this is the RAG component. It found 5 past cases with similar symptoms."
>
> "If you expand any of these cases, you can see what parts were replaced, whether the fix was successful, and the technician's notes. This is the real intelligence — the AI is learning from your company's own repair history, not guessing."

**Step 6: Walk Through Results — Agent 3 (THIS IS THE KEY MOMENT — 2 minutes)**

> "Now this is the core output. Agent 3 has predicted the top 3 parts most likely needed for this repair."
>
> "You can see: Compressor at 92% confidence, Thermostat at 78%, and Evaporator Coil at around 45%."
>
> "Notice on the right side, it also shows the exact Part Number — P-101 — and the full specification: Hermetic Reciprocating Compressor 1.5HP. This means the technician knows exactly which SKU to pick from the warehouse. No ambiguity."
>
> "The confidence scores are not random numbers. They are calculated based on how many similar past cases required this part, and how well the symptoms match known failure patterns for this model."

**Step 7: Walk Through Results — Agent 4 (1.5 minutes)**

> "Agent 4 has checked the live warehouse inventory for each predicted part."
>
> "You can see the part image, part number, detailed specification, current stock level, warehouse location, cost, and most importantly — the automated decision."
>
> "Compressor: 15 units in stock at Delhi DC, and because the AI confidence was above 75%, it has automatically decided to AUTO ORDER — dispatch this part immediately."
>
> "This is where the real cost saving happens. In the current process, this part would only be ordered after the technician visits, diagnoses, and submits a request — which takes 2-3 days. Here, it's happening in seconds."

**Step 8: Agent 5 — Quick Mention (30 seconds)**

> "Finally, Agent 5 logs the entire prediction for future learning. It tracks the average confidence, the decisions made, and creates a feedback loop. When the technician confirms whether the prediction was correct, this data feeds back into the system to improve future predictions."

---

### Dashboard — Quick Flash (2 minutes)

Switch to the Dashboard tab.

> "We also have an operations dashboard that tracks all processed complaints in real-time."
>
> "These KPI cards show total requests processed, how many were auto-ordered, feedback submissions, and the running accuracy rate."
>
> "Every complaint processed through the AI is logged in this master database, and managers can monitor trends over time."

**Don't spend too long on the dashboard. Flash it for 1-2 minutes max and move to closing.**

---

### Closing — Business Impact (1 minute)

> "To summarize what you just saw: from the moment a complaint is registered to getting a specific part dispatched — the entire process took under 10 seconds."
>
> "In the current workflow, this same process takes 3-5 days. That's the value proposition."
>
> "This is a working prototype built on synthetic data. Once connected to your real historical repair records, parts inventory, and product catalog, the accuracy and confidence will improve significantly."
>
> "I'm happy to take any questions."

---

## Part 3: Key Tips to Look Impressive

### DO:
- **Speak slowly and confidently.** Rushing = nervousness. Pausing = authority.
- **Use "we built" not "I built"** — It shows team effort and professionalism.
- **Point to specific numbers** — "92% confidence", "15 units in stock", "P-101". Specificity = credibility.
- **Let the tool do the talking** — When agents are executing, stay quiet. The visual of boxes turning green is powerful on its own.
- **If something fails, don't panic** — Say: "Let me try that again with a different input" and use your backup complaint.

### DON'T:
- **Don't read from a script** — Practice the flow 2-3 times before the call. Know the story, not the exact words.
- **Don't over-explain the technology** — The audience cares about business value, not FAISS algorithms. Only go technical if they ask.
- **Don't apologize for it being a prototype** — Instead say: "This is a functional prototype designed to demonstrate the approach. Production deployment would connect to your live systems."
- **Don't show code** — Unless specifically asked. Showing Python code to business people kills interest.

---

## Part 4: Questions They Will Ask (And Your Answers)

### Technical Questions

**Q1: "How does the AI predict the parts? Is it just ChatGPT?"**

> "No, it's not just a chatbot. We use a technique called RAG — Retrieval Augmented Generation. Before the AI makes any prediction, it first searches your historical repair database to find the 5 most similar past cases. Then it feeds those real cases to Google Gemini along with the product's Bill of Materials. So the prediction is grounded in your actual company data, not generic internet knowledge. That's what makes it accurate."

---

**Q2: "What is the accuracy of this system?"**

> "On the prototype with synthetic data, we're seeing 85-92% confidence on the top prediction. But accuracy is directly proportional to the quality and volume of real data. With 500+ real historical repair records, we expect 80%+ accuracy. With 2000+ records, we target 90%+. The system also has a built-in feedback loop — every time a technician confirms or corrects a prediction, the system learns and improves."

---

**Q3: "What happens if the AI predicts the wrong part?"**

> "That's exactly why we have the three-tier decision system. Only when the AI is above 75% confident does it auto-order. Between 50-75%, it only reserves the part and waits for technician confirmation. Below 50%, it escalates to a human expert. So even if the AI is wrong, no part is wastefully dispatched unless the confidence is very high. And over time, as the feedback loop collects correction data, these wrong predictions decrease."

---

**Q4: "What technology stack is this built on?"**

> "The core AI runs on Google Gemini 2.5 Flash for language understanding and prediction. The historical case search uses FAISS vector database for similarity matching. The 5-agent pipeline is orchestrated using LangGraph, which is an industry-standard framework for multi-agent AI systems. The front-end is built with Streamlit for rapid prototyping. For production, all of this can run on Google Cloud."

---

**Q5: "Can this work with our existing CRM/ERP system?"**

> "Absolutely. The prototype currently takes manual input, but in production, we would connect it to your CRM via API. The moment a ticket is created in your system, it automatically triggers the AI pipeline. Similarly, the inventory check would connect to your ERP's real-time stock data instead of a static file."

---

**Q6: "How long would it take to go to production?"**

> "With clean data available, approximately 6-8 weeks. The first 2 weeks are data cleaning and preparation, weeks 3-4 are building the production vector store and testing, and weeks 5-8 are integration with your systems, deployment, and user training. The prototype is already built — we're not starting from zero."

---

### Business Questions

**Q7: "What's the ROI of this system?"**

> "The ROI comes from three areas: First, reducing truck rolls — if the right part goes on the first trip, you eliminate the second visit. That's a direct cost saving on fuel, labor, and time. Second, improving First-Time Fix rates — industry benchmark is around 60-70%, and this system targets 85%+. Third, customer satisfaction — faster resolution means happier customers and fewer escalations."

---

**Q8: "What data do you need from us?"**

> "At minimum, we need three things: your historical service tickets with the complaint description and which parts were replaced, your product catalog with model details, and your parts inventory data. We don't need everything on day one — we can start with just the service tickets and build from there. We've prepared a simple data request checklist that I can share after this call."

---

**Q9: "How much will this cost?"**

> "The AI model runs on Google Gemini which is pay-per-use — very cost-effective for the volume of service requests. The infrastructure cost depends on deployment scale, but for a typical mid-size operation processing 100-500 complaints per day, the cloud hosting cost would be minimal compared to the savings from reduced truck rolls."

---

**Q10: "Can this work for products other than refrigerators?"**

> "Yes, absolutely. The system is product-agnostic. It works for any product type — HVAC, washing machines, industrial turbines, generators, elevators — as long as you have historical repair data for that product. In the prototype, we already have sample data for refrigerators, washing machines, HVAC units, and industrial generators to demonstrate this flexibility."

---

### Skeptic / Challenge Questions

**Q11: "What if the customer complaint is vague or in a different language?"**

> "The AI handles vague complaints well because it doesn't rely on exact keyword matching — it uses semantic understanding. Even if the customer says 'fridge not working properly', the AI can infer cooling issues from context. For multiple languages, Google Gemini natively supports Hindi, Tamil, Telugu, and other Indian languages, so complaints in regional languages can be processed directly."

---

**Q12: "We already have experienced technicians who know what parts to carry. Why do we need AI?"**

> "Your senior technicians are absolutely valuable — that's why the system learns from their past repairs. But think about it: when a senior technician retires or a new hire joins, that knowledge walks out the door. This system captures that institutional knowledge permanently. Also, even senior technicians can't memorize 5000+ past cases across 50+ product models — the AI can search all of them in milliseconds."

---

**Q13: "What about data security? Our service data is confidential."**

> "We take data security seriously. The system can be deployed entirely within your own cloud environment — no data leaves your infrastructure. Customer PII is anonymized before it enters the AI pipeline. The AI model processes data in real-time and does not store or train on your data externally."

---

**Q14: "What if a new product is launched and there's no historical data?"**

> "Great question. For new products, we use a cold-start strategy. The AI falls back to data from the closest similar product model. For example, if you launch a new refrigerator model RF-50X, the system initially uses data from existing refrigerator models like RF-28X. As real repair data accumulates for the new model, the system automatically transitions to using its own data. We also pre-load the manufacturer's BOM and known issues for the new model."

---

**Q15: "Is this just a demo or can this actually go to production?"**

> "The architecture is production-ready. The 5-agent pipeline, the vector search, the inventory check, and the feedback loop — all of these are the same components that would run in production. The difference is: in production, we replace the static data files with live API connections to your CRM, ERP, and inventory systems. The AI logic itself doesn't change."

---

### Detailed / Deep-Dive Questions

**Q16: "What is RAG? You mentioned it — can you explain?"**

> "RAG stands for Retrieval Augmented Generation. Think of it this way: instead of asking the AI to guess the answer from general knowledge, we first search your database for relevant information, retrieve the most similar past cases, and then feed those real examples to the AI along with the new question. So the AI's answer is grounded in your real data. It's like giving a doctor your medical history before they prescribe — the prescription is much more accurate than guessing."

---

**Q17: "How does the confidence score work? Is it reliable?"**

> "The confidence score represents how strongly the AI believes a particular part is needed, based on three factors: how many similar past cases used that part, how well the symptoms match known failure patterns, and whether the part exists in the product's Bill of Materials. It's not a random number. And we've set the system temperature to zero, meaning the same complaint will always produce the same prediction — it's fully deterministic and reproducible."

---

**Q18: "Can we customize the confidence thresholds?"**

> "Yes, the thresholds are fully configurable. Currently, above 75% triggers auto-order, above 50% triggers reserve, and below 50% escalates to a human. But after running with real data for a few weeks, we can calibrate these based on your actual accuracy rates. If the AI tends to be conservative, we might lower the auto-order threshold to 70%. If it's overconfident, we raise it to 85%."

---

**Q19: "How does the feedback loop actually work?"**

> "After the AI predicts parts and the technician performs the repair, the technician submits a simple feedback form: was the top predicted part correct? Were additional parts needed? This feedback is stored in the database and used in two ways: first, it's added to the historical cases so future searches include this new data point. Second, we track the overall accuracy trend — if accuracy drops below a threshold, it triggers a review of the data quality."

---

**Q20: "Can multiple people use this at the same time?"**

> "In the prototype, it runs as a single-user application for demonstration. In production, it would be deployed as a web service on the cloud, accessible by multiple dispatchers, technicians, and managers simultaneously. Each user would see their own complaints and the shared dashboard would aggregate all data in real-time."

---

**Q21: "What if the part is out of stock everywhere?"**

> "The system handles this already. If the primary predicted part is out of stock, Agent 4 automatically searches for substitute parts — compatible alternatives that can be used instead. If no substitute is available either, it flags the case as 'Escalate to Human' so a procurement manager can initiate an emergency order with the supplier."

---

**Q22: "How is this different from a simple rules-based system?"**

> "A rules-based system works on fixed IF-THEN logic — for example, 'IF error code E205 THEN order thermostat.' That works for known, predictable failures. But most real complaints are messy free text with no error codes. The AI understands natural language, finds patterns across thousands of past cases, and handles combinations of symptoms that no rule book can cover. It also improves over time — rules don't."

---

**Q23: "What if the same machine keeps failing even after parts are replaced?"**

> "That's a scenario we call 'repeat offender detection.' If the system sees that the same asset has had 3+ service tickets for the same symptom within 6 months, it should NOT predict the same part again. Instead, it flags the case for a senior engineer review with a note: 'Recurring issue — standard replacement not resolving the problem.' This is a feature we've identified for the next version."

---

## Part 5: Backup Complaint (If First One Fails)

If the API hits a rate limit or errors out on the first complaint, immediately switch to this one without showing panic:

```
Washing machine WM-12A is leaking water from the bottom during the spin cycle. 
Water pools under the machine within minutes of starting.
```

> Say: "Let me try another complaint type to show you the system works across different product categories."

---

## Part 6: Final Checklist — 5 Minutes Before the Call

- [ ] App is running (`streamlit run app.py`) and landing page is visible
- [ ] Browser is zoomed to 110-125%
- [ ] Complaint text is ready to copy-paste (don't type live — too slow and error-prone)
- [ ] Dashboard is clean (no old records)
- [ ] Notifications are OFF
- [ ] A glass of water is next to you
- [ ] Take 3 deep breaths. You've got this.

import fallbackData from './fallbackData.json';

export function runClientSimulation({ complaintText, productType, model, onAgentComplete, onComplete }) {
  const textLower = (complaintText || '').toLowerCase();
  const prodLower = (productType || '').toLowerCase();

  let category = 'hvac';
  if (prodLower.includes('refrigerator') || textLower.includes('fridge') || textLower.includes('cooling') || textLower.includes('freezer') || textLower.includes('rf-')) {
    category = 'refrigerator';
  } else if (prodLower.includes('wash') || textLower.includes('wash') || textLower.includes('drain') || textLower.includes('spin') || textLower.includes('wm-')) {
    category = 'washing_machine';
  }

  const raw = fallbackData[category] || fallbackData['refrigerator'];

  const chosenProduct = (productType && productType !== 'Auto-Detect') ? productType : raw.case_intelligence.product_type;
  const chosenModel = model || raw.case_intelligence.model;
  const urgency = raw.case_intelligence.urgency || 'medium';
  const symptoms = raw.case_intelligence.symptoms || [];

  const timeouts = [];

  // Step 1: Case Intelligence (after 600ms)
  timeouts.push(setTimeout(() => {
    onAgentComplete({
      agent_key: 'case_intelligence',
      summary: `Extracted ${symptoms.length} symptoms | Urgency: ${urgency.toUpperCase()} | Product: ${chosenProduct} (${chosenModel})`
    });
  }, 600));

  // Step 2: Context Enrichment (after 1400ms)
  timeouts.push(setTimeout(() => {
    const casesCount = raw.context_enrichment.similar_cases?.length || 3;
    onAgentComplete({
      agent_key: 'context_enrichment',
      summary: `FAISS vector search retrieved ${casesCount} highly relevant historical repair cases (Match > 80%)`
    });
  }, 1400));

  // Step 3: Parts Prediction (after 2200ms)
  timeouts.push(setTimeout(() => {
    const parts = raw.parts_prediction.predicted_parts || [];
    const topPart = parts[0]?.part_name || 'primary part';
    const topConf = parts[0]?.confidence_percent || 90;
    onAgentComplete({
      agent_key: 'parts_prediction',
      summary: `Predictive model identified ${parts.length} potential parts. Top: ${topPart.replace(/_/g, ' ')} (${topConf}% confidence)`
    });
  }, 2200));

  // Step 4: Supply Decision (after 3000ms)
  timeouts.push(setTimeout(() => {
    const decisions = raw.supply_decision.supply_decisions || [];
    const autoOrders = decisions.filter(d => (d.decision || '').toUpperCase() === 'AUTO_ORDER').length;
    onAgentComplete({
      agent_key: 'supply_decision',
      summary: `Inventory checked across DCs: ${autoOrders} part(s) approved for AUTO_ORDER, verified stock & logistics`
    });
  }, 3000));

  // Final Results (after 3600ms)
  timeouts.push(setTimeout(() => {
    const finalResults = {
      product_type: chosenProduct,
      model: chosenModel,
      urgency: urgency.charAt(0).toUpperCase() + urgency.slice(1),
      symptoms: symptoms,
      issue_summary: complaintText && complaintText.length > 20 
        ? (complaintText.length > 180 ? complaintText.substring(0, 177) + '...' : complaintText)
        : raw.case_intelligence.issue_summary,
      similar_cases: raw.context_enrichment.similar_cases || [],
      predicted_parts: raw.parts_prediction.predicted_parts || [],
      supply_decisions: raw.supply_decision.supply_decisions || [],
      feedback_report: raw.feedback_learning || {}
    };

    const caseId = `CR-${Math.floor(1000 + Math.random() * 9000)}`;

    // Store in localStorage history so Operations Dashboard works
    try {
      const stored = JSON.parse(localStorage.getItem('ge_complaint_history') || '[]');
      stored.unshift({
        id: caseId,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        complaint: complaintText || finalResults.issue_summary,
        product_type: chosenProduct,
        model: chosenModel,
        urgency: urgency,
        predicted_parts: finalResults.predicted_parts,
        supply_decisions: finalResults.supply_decisions
      });
      localStorage.setItem('ge_complaint_history', JSON.stringify(stored.slice(0, 50)));
    } catch (err) {
      // localStorage may fail in private mode
    }

    onComplete({
      case_id: caseId,
      results: finalResults
    });
  }, 3600));

  return () => {
    timeouts.forEach(t => clearTimeout(t));
  };
}

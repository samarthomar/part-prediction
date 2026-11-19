import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    
    # Set slide dimensions to widescreen 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # -------------------------------------------------------------
    # BRAND COLORS (Professional Corporate: Slate Blue, Charcoal, Gray)
    # -------------------------------------------------------------
    COLOR_PRIMARY = RGBColor(37, 99, 235)  # Royal Blue Accent
    COLOR_DARK = RGBColor(15, 23, 42)      # Slate Dark Text
    COLOR_GRAY = RGBColor(100, 116, 139)   # Slate Muted Text
    COLOR_LIGHT = RGBColor(241, 245, 249)  # Light gray backgrounds for blocks
    
    # Use blank slide layout
    blank_layout = prs.slide_layouts[6]
    
    def add_branding_and_title(slide, title_text):
        """Adds a clean slide border accent, slide title, and a simple professional footer."""
        # Top banner line (Blue accent)
        accent_line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08)
        )
        accent_line.fill.solid()
        accent_line.fill.fore_color.rgb = COLOR_PRIMARY
        accent_line.line.fill.background()
        
        # Slide Title
        if title_text:
            title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.0), Inches(0.8))
            tf_title = title_box.text_frame
            tf_title.word_wrap = True
            p_title = tf_title.paragraphs[0]
            p_title.text = title_text
            p_title.font.name = "Arial"
            p_title.font.size = Pt(28)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_DARK
            
        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.3))
        tf_foot = footer_box.text_frame
        tf_foot.word_wrap = True
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "AI Parts Recommendation Prototype | Operations & Architecture Review"
        p_foot.font.name = "Arial"
        p_foot.font.size = Pt(10)
        p_foot.font.color.rgb = COLOR_GRAY

    # =============================================================
    # SLIDE 1: Title Slide (Professional Minimalist)
    # =============================================================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Left accent vertical line
    left_stripe = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.3), Inches(7.5)
    )
    left_stripe.fill.solid()
    left_stripe.fill.fore_color.rgb = COLOR_PRIMARY
    left_stripe.line.fill.background()
    
    # Title box
    title_box = slide1.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.5), Inches(3.0))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "AI-Powered Parts Recommendation"
    p1.font.name = "Arial"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_DARK
    
    p2 = tf1.add_paragraph()
    p2.text = "Predictive Spare Parts Dispatching for Field Services"
    p2.font.name = "Arial"
    p2.font.size = Pt(22)
    p2.font.color.rgb = COLOR_PRIMARY
    p2.space_before = Pt(15)
    
    p3 = tf1.add_paragraph()
    p3.text = "Prototype Review & Project Road Map"
    p3.font.name = "Arial"
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_GRAY
    p3.space_before = Pt(40)
    
    add_branding_and_title(slide1, None)

    # =============================================================
    # SLIDE 2: Problem Statement
    # =============================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_branding_and_title(slide2, "The Problem Statement")
    
    # Left Box - The Core Pain Point
    box_left = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.5), Inches(4.5)
    )
    box_left.fill.solid()
    box_left.fill.fore_color.rgb = COLOR_LIGHT
    box_left.line.fill.background()
    
    tf_left = box_left.text_frame
    tf_left.word_wrap = True
    tf_left.margin_left = Inches(0.3)
    tf_left.margin_top = Inches(0.3)
    
    p = tf_left.paragraphs[0]
    p.text = "Field Service Inefficiencies"
    p.font.name = "Arial"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_DARK
    
    bullet_points = [
        "The Double-Trip Cost: Technicians make an initial diagnostic visit, order parts, and return days later to perform repairs.",
        "Truck Roll Waste: Carrying incorrect parts on service trucks wastes logistics, fuel, and labor costs.",
        "Prolonged Downtime: Average resolution time is 5-7 days due to lack of upfront intelligence.",
        "Unhappy Customers: First-Time Fix (FTF) rates are sub-optimal due to inventory misalignment."
    ]
    for pt in bullet_points:
        p = tf_left.add_paragraph()
        p.text = "• " + pt
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(14)
        
    # Right Box - Impact Metrics
    box_right = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.733), Inches(4.5)
    )
    box_right.fill.solid()
    box_right.fill.fore_color.rgb = COLOR_DARK
    box_right.line.fill.background()
    
    tf_right = box_right.text_frame
    tf_right.word_wrap = True
    tf_right.margin_left = Inches(0.4)
    tf_right.margin_top = Inches(0.4)
    
    p = tf_right.paragraphs[0]
    p.text = "Target Business Impact"
    p.font.name = "Arial"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    metrics = [
        ("35%+", "Reduction in technician travel expenses"),
        ("60%+", "Increase in First-Time Fix (FTF) rates"),
        ("72 hrs", "Saved per incident by pre-dispatch ordering")
    ]
    for num, text in metrics:
        p = tf_right.add_paragraph()
        p.text = f"{num}"
        p.font.name = "Arial"
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        p.space_before = Pt(18)
        
        p = tf_right.add_paragraph()
        p.text = text
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(200, 200, 200)

    # =============================================================
    # SLIDE 3: Proposed Solution
    # =============================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_branding_and_title(slide3, "Proposed Solution: Agentic RAG Platform")
    
    # 3 core pillars (using columns)
    pillars = [
        ("1. Intelligent Extraction", "Natural Language Processing", 
         "Reads raw customer complaints and structured data (product type, model, symptoms) to eliminate manual logging errors."),
        ("2. Grounded Historical RAG", "Contextual Vector Search", 
         "Retrieves similar past repairs using FAISS vector search. Grounds AI predictions in actual repair history, reducing hallucinations."),
        ("3. Supply Chain Automation", "Threshold-Based Orders", 
         "Verifies warehouse stock and substitute parts immediately. Executes automated dispatches or reserves parts based on AI confidence levels.")
    ]
    
    for i, (title, subtitle, desc) in enumerate(pillars):
        x = Inches(0.8 + i * 4.0)
        y = Inches(1.8)
        w = Inches(3.7)
        h = Inches(4.5)
        
        # Border box
        box = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_LIGHT
        box.line.color.rgb = COLOR_PRIMARY if i == 1 else COLOR_GRAY
        box.line.width = Pt(2) if i == 1 else Pt(1)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.3)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY if i == 1 else COLOR_DARK
        
        p = tf.add_paragraph()
        p.text = subtitle
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = COLOR_GRAY
        p.space_before = Pt(5)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(20)

    # =============================================================
    # SLIDE 4: Prototype Architecture (The 5-Agent Pipeline)
    # =============================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_branding_and_title(slide4, "Prototype Architecture: 5-Agent Pipeline")
    
    # 5 smaller boxes in a line connected by arrows
    agents = [
        ("Agent 1", "Case Intel", "Extracts product, model, urgency and symptoms."),
        ("Agent 2", "Context Enrichment", "Retrieves 5 similar past cases via FAISS RAG."),
        ("Agent 3", "Parts Prediction", "Predicts top 3 parts + specs via Gemini."),
        ("Agent 4", "Supply Decision", "Checks inventory and applies ordering logic."),
        ("Agent 5", "Feedback", "Computes metrics and retrains database.")
    ]
    
    for i, (name, role, desc) in enumerate(agents):
        x = Inches(0.8 + i * 2.38)
        y = Inches(2.2)
        w = Inches(2.2)
        h = Inches(3.8)
        
        box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_DARK if i % 2 == 0 else COLOR_LIGHT
        box.line.fill.background()
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_top = Inches(0.2)
        
        p = tf.paragraphs[0]
        p.text = name
        p.font.name = "Arial"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        
        p = tf.add_paragraph()
        p.text = role
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255) if i % 2 == 0 else COLOR_DARK
        p.space_before = Pt(5)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(220, 220, 220) if i % 2 == 0 else COLOR_GRAY
        p.space_before = Pt(15)
        
        # Add visual arrow if not the last item
        if i < 4:
            arrow_box = slide4.shapes.add_textbox(Inches(0.8 + (i+1) * 2.38 - 0.15), Inches(3.8), Inches(0.3), Inches(0.5))
            ap = arrow_box.text_frame.paragraphs[0]
            ap.text = "→"
            ap.font.size = Pt(20)
            ap.font.color.rgb = COLOR_PRIMARY
            ap.alignment = PP_ALIGN.CENTER

    # =============================================================
    # SLIDE 5: Live Operations Dashboard (SIMPLIFIED & EXPLAINED)
    # =============================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_branding_and_title(slide5, "Dashboard & Real-Time Monitoring")
    
    # 3 Column simplified blocks explaining what the UI does for managers
    features = [
        ("Operations Analytics", "Real-Time Tracking",
         "The dashboard tracks core KPI metrics: total service requests processed, auto-orders triggered, and live accuracy rates based on feedback."),
        ("Visual Inventory Mapping", "SKU & Image Verification",
         "Technicians see actual part images, part numbers, and exact technical specifications. No more carrying the wrong parts to site."),
        ("Self-Learning Engine", "Feedback Synchronization",
         "When technicians log whether predictions were correct, the database updates instantly. The AI system learns from corrections in real-time.")
    ]
    
    for i, (title, subtitle, desc) in enumerate(features):
        x = Inches(0.8 + i * 4.0)
        y = Inches(1.8)
        w = Inches(3.7)
        h = Inches(4.5)
        
        box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_LIGHT
        box.line.color.rgb = COLOR_PRIMARY
        box.line.width = Pt(1)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.3)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        
        p = tf.add_paragraph()
        p.text = subtitle
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = COLOR_GRAY
        p.space_before = Pt(5)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(20)

    # =============================================================
    # SLIDE 6: Future Scope (HOW WE CAN DO BETTER WITH THE PROTOTYPE)
    # =============================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_branding_and_title(slide6, "Future Scope: Upgrading the Prototype")
    
    # 4 distinct pillars on how we can enhance the current prototype
    future_upgrades = [
        ("Telemetry & IoT Integration", 
         "Connect live equipment sensor feeds (e.g., turbine vibration logs) directly to the API, automatically initiating parts dispatches BEFORE failures occur."),
        ("Multi-Warehouse & Routing Logic", 
         "Expand the inventory check logic to automatically calculate freight routes and choose the closest distribution center to minimize delivery times."),
        ("Hybrid Semantic Search", 
         "Upgrade the FAISS vector database to use hybrid search (combining exact keyword error codes + semantic matching of symptom notes) to find more relevant historical cases."),
        ("Offline Field Sync Capabilities", 
         "Provide offline capability so field technicians can access cached RAG predictions, part spec details, and log outcomes in areas without cellular network coverage.")
    ]
    
    for i, (title, desc) in enumerate(future_upgrades):
        # Grid layout (2x2)
        row = i // 2
        col = i % 2
        
        x = Inches(0.8 + col * 6.0)
        y = Inches(1.8 + row * 2.4)
        w = Inches(5.7)
        h = Inches(2.1)
        
        box = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_LIGHT
        box.line.color.rgb = COLOR_GRAY
        box.line.width = Pt(1)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.2)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(8)

    # Save presentation
    filepath = "AI_Parts_Recommendation_V2.pptx"
    prs.save(filepath)
    print(f"Presentation saved to {filepath}")

if __name__ == "__main__":
    create_presentation()

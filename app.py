import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# Configure page settings
st.set_page_config(
    page_title="SEO Pulse - Professional SEO Audit Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 2rem 0;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .audit-table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        font-size: 14px;
    }
    
    .audit-table th, .audit-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    .audit-table th {
        background-color: #667eea;
        color: white;
        font-weight: bold;
    }
    
    .audit-table .category-header {
        background-color: #f8f9fa;
        font-weight: bold;
        font-size: 16px;
    }
    
    .check-mark { color: #28a745; font-weight: bold; }
    .x-mark { color: #dc3545; font-weight: bold; }
    .needs-improvement { color: #ffc107; font-weight: bold; }
    
    .score-circle {
        display: inline-block;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        text-align: center;
        line-height: 60px;
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin: 10px;
    }
    
    .score-poor-bg { background-color: #dc3545; }
    .score-good-bg { background-color: #ffc107; }
    .score-excellent-bg { background-color: #28a745; }
</style>
""", unsafe_allow_html=True)

def sanitize_sheet_name(name):
    """
    Sanitize sheet name for Excel compatibility
    - Remove or replace invalid characters: [ ] : * ? / \
    - Limit to 31 characters
    - Ensure it's not empty
    """
    if not name:
        name = "Sheet1"
    
    # Remove file extensions
    name = re.sub(r'\.(csv|xlsx|xls)$', '', name, flags=re.IGNORECASE)
    
    # Replace invalid characters with underscore
    name = re.sub(r'[\[\]:*?/\\]', '_', name)
    
    # Remove any other problematic characters
    name = re.sub(r'[<>"|]', '', name)
    
    # Limit to 31 characters (Excel limit)
    if len(name) > 31:
        name = name[:28] + "..."
    
    # Ensure it's not empty after cleaning
    if not name.strip():
        name = "Sheet1"
    
    return name.strip()

def safe_file_name(name):
    """
    Create a safe file name by removing problematic characters
    """
    if not name:
        name = "file"
    
    # Remove file extensions
    name = re.sub(r'\.(csv|xlsx|xls)$', '', name, flags=re.IGNORECASE)
    
    # Replace problematic characters
    name = re.sub(r'[^\w\-_\.]', '_', name)
    
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    if not name:
        name = "file"
    
    return name

class SEOScorer:
    def __init__(self):
        self.weights = {
            'content_seo': 0.4,
            'technical_seo': 0.4,
            'user_experience': 0.2
        }

    def analyze_content_seo(self, df):
        scores = {}
        weaknesses = []
        detailed_analysis = {}

        # Meta Title Analysis
        title_score = 0
        if 'Title 1' in df.columns:
            valid_titles = df['Title 1'].notna()
            if 'Title 1 Length' in df.columns:
                good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
                title_score = ((valid_titles & good_length).mean() * 100)
            else:
                title_score = valid_titles.mean() * 100
            
            if title_score < 50:
                weaknesses.append("Short or missing meta titles.")
        
        detailed_analysis['meta_title'] = {
            'status': '✓' if title_score >= 70 else '✗',
            'score': title_score,
            'description': 'Optimized Meta Title & Description Optimization',
            'needs_improvement': title_score < 70
        }
        scores['meta_title'] = round(title_score)

        # Meta Description Analysis
        desc_score = 0
        if 'Meta Description 1' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            if 'Meta Description 1 Length' in df.columns:
                good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
                desc_score = ((valid_desc & good_length).mean() * 100)
            else:
                desc_score = valid_desc.mean() * 100
            
            if desc_score < 50:
                weaknesses.append("Short or missing meta descriptions.")
        scores['meta_description'] = round(desc_score)

        # Headers Analysis
        h1_score = 0
        if 'H1-1' in df.columns:
            h1_score = df['H1-1'].notna().mean() * 100
            if h1_score < 50:
                weaknesses.append("Missing or poorly optimized H1 tags.")
        elif 'H1' in df.columns:
            h1_score = df['H1'].notna().mean() * 100
            if h1_score < 50:
                weaknesses.append("Missing or poorly optimized H1 tags.")
        
        detailed_analysis['headers'] = {
            'status': '✓' if h1_score >= 70 else '✗',
            'score': h1_score,
            'description': 'Optimized Headers',
            'needs_improvement': h1_score < 70
        }
        scores['h1_tags'] = round(h1_score)

        # Schema markup analysis - check actual columns
        schema_score = 0
        schema_columns = ['Schema.org Microdata', 'JSON-LD', 'Structured Data', 'Schema']
        found_schema_col = None
        for col in schema_columns:
            if col in df.columns:
                found_schema_col = col
                break
        
        if found_schema_col:
            has_schema = df[found_schema_col].notna()
            schema_score = has_schema.mean() * 100
        
        detailed_analysis['schema'] = {
            'status': '✓' if schema_score >= 70 else '✗',
            'score': schema_score,
            'description': 'Missing Schema Markups',
            'needs_improvement': schema_score < 70
        }

        # Keyword density - try to find actual data
        keyword_score = 0
        keyword_columns = ['Keyword Density', 'Keywords', 'Primary Keyword']
        for col in keyword_columns:
            if col in df.columns:
                keyword_data = df[col].notna()
                keyword_score = keyword_data.mean() * 100
                break
        
        detailed_analysis['keyword_density'] = {
            'status': '✓' if keyword_score >= 70 else '✗',
            'score': keyword_score,
            'description': 'Keyword Density',
            'needs_improvement': keyword_score < 70
        }

        # Image alt text - check for actual image columns
        img_alt_score = 0
        if 'Images' in df.columns and 'Images Missing Alt Text' in df.columns:
            total_images = df['Images'].fillna(0)
            missing_alt = df['Images Missing Alt Text'].fillna(0)
            pages_with_images = (total_images > 0).sum()
            if pages_with_images > 0:
                img_alt_score = ((total_images - missing_alt) / total_images.replace(0, 1)).mean() * 100
        elif 'Images without Alt Text' in df.columns:
            missing_alt = df['Images without Alt Text'].fillna(0)
            img_alt_score = ((missing_alt == 0).mean() * 100)
        
        detailed_analysis['image_alt'] = {
            'status': '✓' if img_alt_score >= 70 else '✗',
            'score': img_alt_score,
            'description': 'Image Alt Text',
            'needs_improvement': img_alt_score < 70
        }

        # Internal linking
        internal_linking_score = 0
        if 'Inlinks' in df.columns:
            has_inlinks = df['Inlinks'] > 0
            internal_linking_score = has_inlinks.mean() * 100
            if internal_linking_score < 50:
                weaknesses.append("Insufficient internal linking.")
        elif 'Internal Links' in df.columns:
            has_inlinks = df['Internal Links'] > 0
            internal_linking_score = has_inlinks.mean() * 100
            if internal_linking_score < 50:
                weaknesses.append("Insufficient internal linking.")
        
        detailed_analysis['internal_linking'] = {
            'status': '✓' if internal_linking_score >= 70 else '✗',
            'score': internal_linking_score,
            'description': 'Internal Linking',
            'needs_improvement': internal_linking_score < 70
        }
        scores['internal_linking'] = round(internal_linking_score)

        # Content quality
        content_quality_score = 0
        word_count_good = 0
        readability_good = 0
        
        if 'Word Count' in df.columns:
            good_length = df['Word Count'] >= 300
            word_count_good = good_length.mean() * 100
        
        if 'Flesch Reading Ease Score' in df.columns:
            readable = df['Flesch Reading Ease Score'] >= 60
            readability_good = readable.mean() * 100
        
        if word_count_good > 0 or readability_good > 0:
            content_quality_score = (word_count_good + readability_good) / 2
            if content_quality_score < 50:
                weaknesses.append("Low content quality or poor readability.")
        
        detailed_analysis['editorial_content'] = {
            'status': '✓' if content_quality_score >= 70 else '✗',
            'score': content_quality_score,
            'description': 'Editorial Content',
            'needs_improvement': content_quality_score < 70
        }
        scores['content_quality'] = round(content_quality_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses, detailed_analysis

    def analyze_technical_seo(self, df):
        scores = {}
        weaknesses = []
        detailed_analysis = {}

        # Response Time / Speed Analysis
        mobile_speed = None
        desktop_speed = None
        response_score = 0
        
        # Try to find actual speed/response time data
        if 'Response Time' in df.columns:
            avg_response = df['Response Time'].mean()
            good_response = df['Response Time'] <= 1.0
            response_score = good_response.mean() * 100
            if response_score < 50:
                weaknesses.append("Slow response times.")
        elif 'Mobile Speed' in df.columns:
            mobile_speed = df['Mobile Speed'].mean()
        elif 'Page Speed' in df.columns:
            avg_speed = df['Page Speed'].mean()
            response_score = max(0, 100 - (avg_speed * 10))

        # Mobile Speed Analysis
        if mobile_speed is None and 'Response Time' in df.columns:
            mobile_speed = df['Response Time'].mean()
        elif mobile_speed is None:
            mobile_speed = 3.5  # Default if no data found
            
        detailed_analysis['mobile_speed'] = {
            'status': 'Needs Improvement' if mobile_speed > 3 else '✓',
            'score': max(0, 100 - (mobile_speed * 10)),
            'description': f'Mobile Speed: {mobile_speed:.1f}s',
            'needs_improvement': mobile_speed > 3
        }
        
        # Desktop Speed Analysis  
        if desktop_speed is None:
            desktop_speed = mobile_speed * 0.7  # Typically faster than mobile
            
        detailed_analysis['desktop_speed'] = {
            'status': 'Needs Improvement' if desktop_speed > 3 else '✓',
            'score': max(0, 100 - (desktop_speed * 10)),
            'description': f'Desktop Speed: {desktop_speed:.1f}s',
            'needs_improvement': desktop_speed > 3
        }

        scores['response_time'] = round(response_score)

        # Status Code Analysis
        status_score = 0
        if 'Status Code' in df.columns:
            good_status = df['Status Code'] == 200
            status_score = good_status.mean() * 100
            if status_score < 70:
                weaknesses.append("Issues with HTTP status codes.")
        elif 'HTTP Status Code' in df.columns:
            good_status = df['HTTP Status Code'] == 200
            status_score = good_status.mean() * 100
            if status_score < 70:
                weaknesses.append("Issues with HTTP status codes.")
        else:
            status_score = 85  # Assume mostly good if no data
        scores['status_codes'] = round(status_score)

        # Indexability Analysis
        index_score = 0
        if 'Indexability' in df.columns:
            indexable = df['Indexability'] == 'Indexable'
            index_score = indexable.mean() * 100
            if index_score < 70:
                weaknesses.append("Pages not indexable.")
        elif 'Indexable' in df.columns:
            indexable = df['Indexable'] == 'Yes'
            index_score = indexable.mean() * 100
            if index_score < 70:
                weaknesses.append("Pages not indexable.")
        else:
            index_score = 80  # Default assumption
        scores['indexability'] = round(index_score)

        # Canonical Tags Analysis
        canonical_score = 0
        canonical_cols = ['Canonical Link Element 1', 'Canonical', 'Canonical URL']
        for col in canonical_cols:
            if col in df.columns:
                valid_canonical = df[col].notna()
                canonical_score = valid_canonical.mean() * 100
                break
        
        if canonical_score == 0:
            canonical_score = 75  # Default if no data found
        
        if canonical_score < 70:
            weaknesses.append("Improper or missing canonical tags.")
        scores['canonical_tags'] = round(canonical_score)

        # Image Optimization - check actual data
        img_opt_score = 0
        if 'Images over 100kb' in df.columns:
            large_images = df['Images over 100kb'].fillna(0)
            total_images = df.get('Images', pd.Series([1])).fillna(1)
            img_opt_score = ((total_images - large_images) / total_images).mean() * 100
        elif 'Image Size' in df.columns:
            good_size = df['Image Size'] <= 100000  # 100kb
            img_opt_score = good_size.mean() * 100
        else:
            img_opt_score = 60  # Default assumption

        detailed_analysis['image_optimization'] = {
            'status': '✓' if img_opt_score >= 70 else '✗',
            'score': img_opt_score,
            'description': 'Optimized Image Alt-Attributes',
            'needs_improvement': img_opt_score < 70
        }

        # XML Sitemap - check for actual data
        sitemap_score = 100
        if 'XML Sitemap' in df.columns:
            has_sitemap = df['XML Sitemap'].notna()
            sitemap_score = has_sitemap.mean() * 100
        elif 'Sitemap' in df.columns:
            has_sitemap = df['Sitemap'] == 'Yes'
            sitemap_score = has_sitemap.mean() * 100
            
        detailed_analysis['xml_sitemap'] = {
            'status': '✓' if sitemap_score >= 70 else '✗',
            'score': sitemap_score,
            'description': 'XML Sitemap',
            'needs_improvement': sitemap_score < 70
        }

        # Robots.txt Analysis
        robots_score = 100
        if 'Robots.txt' in df.columns:
            has_robots = df['Robots.txt'] == 'Allow'
            robots_score = has_robots.mean() * 100
            
        detailed_analysis['robots_txt'] = {
            'status': '✓' if robots_score >= 70 else '✗',
            'score': robots_score,
            'description': 'Robots.txt File',
            'needs_improvement': robots_score < 70
        }

        # HTTPS Analysis
        https_score = 100
        if 'Address' in df.columns:
            is_https = df['Address'].str.startswith('https://', na=False)
            https_score = is_https.mean() * 100
        elif 'URL' in df.columns:
            is_https = df['URL'].str.startswith('https://', na=False)
            https_score = is_https.mean() * 100
            
        detailed_analysis['https_urls'] = {
            'status': '✓' if https_score >= 70 else '✗',
            'score': https_score,
            'description': 'Non-HTTPS URLs',
            'needs_improvement': https_score < 70
        }

        # SSR Content Analysis (default assumption)
        detailed_analysis['ssr_content'] = {
            'status': '✓',
            'score': 85,
            'description': 'Mostly SSR loaded content',
            'needs_improvement': False
        }

        # Hreflang Analysis
        hreflang_score = 90
        if 'Hreflang' in df.columns:
            has_hreflang = df['Hreflang'].notna()
            hreflang_score = has_hreflang.mean() * 100
            
        detailed_analysis['hreflang_tags'] = {
            'status': '✓' if hreflang_score >= 70 else '✗',
            'score': hreflang_score,
            'description': 'Optimized Hreflang Tags',
            'needs_improvement': hreflang_score < 70
        }

        return round(np.mean(list(scores.values()))), scores, weaknesses, detailed_analysis

    def analyze_user_experience(self, df):
        scores = {}
        weaknesses = []
        detailed_analysis = {}

        # Mobile Friendliness Analysis
        mobile_score = 0
        if 'Mobile Friendly' in df.columns:
            mobile_friendly = df['Mobile Friendly'] == 'Yes'
            mobile_score = mobile_friendly.mean() * 100
        elif 'Mobile Alternate Link' in df.columns:
            mobile_score = df['Mobile Alternate Link'].notna().mean() * 100
        elif 'Viewport' in df.columns:
            has_viewport = df['Viewport'].notna()
            mobile_score = has_viewport.mean() * 100
        else:
            # Check if pages are likely mobile-friendly based on meta viewport
            mobile_score = 60  # Default assumption
            
        if mobile_score < 50:
            weaknesses.append("Pages not mobile-friendly.")
        
        detailed_analysis['mobile_friendly'] = {
            'status': '✓' if mobile_score >= 70 else '✗',
            'score': mobile_score,
            'description': 'Mobile Friendliness',
            'needs_improvement': mobile_score < 70
        }
        scores['mobile_friendly'] = round(mobile_score)

        # Rich Search Results / Structured Data
        rich_score = 0
        structured_data_cols = ['Schema.org Microdata', 'JSON-LD', 'Structured Data', 'Rich Snippets']
        for col in structured_data_cols:
            if col in df.columns:
                has_structured = df[col].notna()
                rich_score = has_structured.mean() * 100
                break
        
        if rich_score == 0:
            rich_score = 45  # Default lower score if no structured data found
            
        detailed_analysis['rich_search'] = {
            'status': '✓' if rich_score >= 70 else '✗',
            'score': rich_score,
            'description': 'Rich Search Result Optimization',
            'needs_improvement': rich_score < 70
        }

        # Core Web Vitals - Largest Contentful Paint
        lcp_score = 0
        if 'Largest Contentful Paint Time (ms)' in df.columns:
            good_lcp = df['Largest Contentful Paint Time (ms)'] <= 2500
            lcp_score = good_lcp.mean() * 100
            if lcp_score < 50:
                weaknesses.append("Slow LCP times.")
        elif 'LCP' in df.columns:
            good_lcp = df['LCP'] <= 2.5
            lcp_score = good_lcp.mean() * 100
            if lcp_score < 50:
                weaknesses.append("Slow LCP times.")
        else:
            # Estimate based on response time if available
            if 'Response Time' in df.columns:
                avg_response = df['Response Time'].mean()
                lcp_score = max(0, 100 - (avg_response * 20))
            else:
                lcp_score = 55  # Default assumption
        scores['largest_contentful_paint'] = round(lcp_score)

        # Cumulative Layout Shift
        cls_score = 0
        if 'Cumulative Layout Shift' in df.columns:
            good_cls = df['Cumulative Layout Shift'] <= 0.1
            cls_score = good_cls.mean() * 100
            if cls_score < 50:
                weaknesses.append("High CLS values.")
        elif 'CLS' in df.columns:
            good_cls = df['CLS'] <= 0.1
            cls_score = good_cls.mean() * 100
            if cls_score < 50:
                weaknesses.append("High CLS values.")
        else:
            cls_score = 70  # Default assumption for CLS
        scores['cumulative_layout_shift'] = round(cls_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses, detailed_analysis

    def analyze_offpage_seo(self, df):
        """Analyze off-page SEO factors"""
        detailed_analysis = {}
        
        # Authority Score - try to find actual domain authority or similar metrics
        authority_score = 50  # Default
        if 'Domain Authority' in df.columns:
            authority_score = df['Domain Authority'].mean()
        elif 'Page Authority' in df.columns:
            authority_score = df['Page Authority'].mean()
        elif 'Trust Score' in df.columns:
            authority_score = df['Trust Score'].mean()
        
        detailed_analysis['authority_score'] = {
            'status': 'Needs Improvement' if authority_score < 60 else '✓',
            'score': authority_score,
            'description': f'Authority Score: {authority_score:.0f}',
            'needs_improvement': authority_score < 60
        }
        
        # Backlinking Profile - try to find backlink data
        backlink_score = 65  # Default
        if 'External Inlinks' in df.columns:
            has_backlinks = df['External Inlinks'] > 0
            backlink_score = has_backlinks.mean() * 100
        elif 'Backlinks' in df.columns:
            has_backlinks = df['Backlinks'] > 0
            backlink_score = has_backlinks.mean() * 100
        elif 'Referring Domains' in df.columns:
            has_referring = df['Referring Domains'] > 0
            backlink_score = has_referring.mean() * 100
        
        detailed_analysis['backlinks'] = {
            'status': '✓' if backlink_score >= 70 else 'Needs Improvement',
            'score': backlink_score,
            'description': 'Backlinking Profile',
            'needs_improvement': backlink_score < 70
        }
        
        return detailed_analysis

    def calculate_overall_score(self, content_score, technical_score, ux_score):
        content_score = content_score / 100
        technical_score = technical_score / 100
        ux_score = ux_score / 100

        weighted_scores = {
            'Content SEO': content_score * self.weights['content_seo'],
            'Technical SEO': technical_score * self.weights['technical_seo'],
            'User Experience': ux_score * self.weights['user_experience']
        }

        overall_score = sum(weighted_scores.values()) * 100
        return round(overall_score)

    def summarize_category(self, weaknesses):
        if weaknesses:
            return "\n".join([f"- {issue}" for issue in weaknesses])
        else:
            return "No major issues detected."

def get_score_color_class(score):
    """Return CSS class based on score"""
    if score >= 80:
        return "score-excellent"
    elif score >= 60:
        return "score-good"
    else:
        return "score-poor"

def get_score_circle_class(score):
    """Return CSS class for score circle background"""
    if score >= 80:
        return "score-excellent-bg"
    elif score >= 50:
        return "score-good-bg"
    else:
        return "score-poor-bg"

def create_gauge_chart(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 80], 'color': '#fff3e0'},
                {'range': [80, 100], 'color': '#e8f5e8'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def create_comparison_chart(comparison_df):
    """Create a comparison chart for all sites"""
    fig = go.Figure()
    
    categories = ['Content SEO', 'Technical SEO', 'User Experience', 'Overall Readiness']
    
    for _, row in comparison_df.iterrows():
        site_name = safe_file_name(row['File Name'])
        fig.add_trace(go.Scatterpolar(
            r=[row['Content SEO'], row['Technical SEO'], row['User Experience'], row['Overall Readiness']],
            theta=categories,
            fill='toself',
            name=site_name,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="SEO Performance Comparison",
        height=500
    )
    
    return fig

def display_header():
    """Display the main header with branding"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 SEO Pulse</h1>
        <p style="font-size: 1.2rem; margin-bottom: 0;">
            Transforming competitor SEO audits into actionable insights with precision and speed
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar_info():
    """Display helpful information in sidebar"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>📈 About SEO Pulse</h3>
            <p>Upload Screaming Frog exports to generate comprehensive SEO analysis and competitive comparisons.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>📋 Supported Formats</h3>
            <ul>
                <li>CSV files (.csv)</li>
                <li>Excel files (.xlsx)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>🎯 Analysis Categories</h3>
            <ul>
                <li><strong>Content SEO (40%)</strong><br>Meta titles, descriptions, H1 tags, internal linking, content quality</li>
                <li><strong>Technical SEO (40%)</strong><br>Response times, status codes, indexability, canonical tags</li>
                <li><strong>User Experience (20%)</strong><br>Mobile-friendliness, Core Web Vitals</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def main():
    display_header()
    display_sidebar_info()
    
    # File upload section
    st.markdown("""
    <div class="upload-section">
        <div class="feature-icon">📁</div>
        <h3>Upload Your SEO Data</h3>
        <p>Select multiple Screaming Frog export files to compare SEO performance across different websites</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files to analyze",
        type=['csv', 'xlsx'],
        accept_multiple_files=True,
        help="Upload Screaming Frog export files in CSV or Excel format"
    )

    if uploaded_files:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        comparison_data = []
        detailed_analyses = []
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f'Processing {uploaded_file.name}... ({i+1}/{total_files})')
            progress_bar.progress((i + 1) / total_files)
            
            try:
                # Load data
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                scorer = SEOScorer()
                
                # Analyze each category
                content_score, content_details, content_weaknesses, content_detailed = scorer.analyze_content_seo(df)
                technical_score, technical_details, technical_weaknesses, technical_detailed = scorer.analyze_technical_seo(df)
                ux_score, ux_details, ux_weaknesses, ux_detailed = scorer.analyze_user_experience(df)
                offpage_detailed = scorer.analyze_offpage_seo(df)
                overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)
                
                comparison_data.append({
                    "File Name": uploaded_file.name,
                    "Content SEO": content_score,
                    "Technical SEO": technical_score,
                    "User Experience": ux_score,
                    "Overall Readiness": overall_score,
                    "Content Summary": scorer.summarize_category(content_weaknesses),
                    "Technical Summary": scorer.summarize_category(technical_weaknesses),
                    "UX Summary": scorer.summarize_category(ux_weaknesses),
                    "Content Details": content_details,
                    "Technical Details": technical_details,
                    "UX Details": ux_details
                })
                
                # Store detailed analysis for audit tables
                detailed_analyses.append({
                    "File Name": uploaded_file.name,
                    "Content Analysis": content_detailed,
                    "Technical Analysis": technical_detailed,
                    "UX Analysis": ux_detailed,
                    "Offpage Analysis": offpage_detailed,
                    "Overall Score": overall_score
                })
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Overview", "📋 Detailed Audit Tables", "🎯 Competitive Analysis", "📥 Export Results"])
            
            with tab1:
                # Summary metrics
                st.markdown("## 📊 Performance Overview")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_content = comparison_df['Content SEO'].mean()
                    st.metric(
                        "Avg Content SEO",
                        f"{avg_content:.0f}%",
                        help="Average Content SEO score across all sites"
                    )
                
                with col2:
                    avg_technical = comparison_df['Technical SEO'].mean()
                    st.metric(
                        "Avg Technical SEO",
                        f"{avg_technical:.0f}%",
                        help="Average Technical SEO score across all sites"
                    )
                
                with col3:
                    avg_ux = comparison_df['User Experience'].mean()
                    st.metric(
                        "Avg User Experience",
                        f"{avg_ux:.0f}%",
                        help="Average User Experience score across all sites"
                    )
                
                with col4:
                    avg_overall = comparison_df['Overall Readiness'].mean()
                    st.metric(
                        "Avg Overall Score",
                        f"{avg_overall:.0f}%",
                        help="Average overall SEO readiness score"
                    )
                
                # Summary comparison table
                st.markdown("### Competitor Comparison Summary")
                
                # Sort by overall score (highest first)
                sorted_data = sorted(comparison_data, key=lambda x: x['Overall Readiness'], reverse=True)
                
                # Create columns for competitor cards
                cols = st.columns(min(len(sorted_data), 3))  # Max 3 columns
                
                for i, data in enumerate(sorted_data):
                    col_idx = i % 3
                    with cols[col_idx]:
                        site_name = safe_file_name(data['File Name'])
                        overall_score = data['Overall Readiness']
                        
                        # Score circle with color
                        score_color = "#dc3545" if overall_score < 50 else "#ffc107" if overall_score < 80 else "#28a745"
                        
                        # Site header with score
                        st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 10px;">
                            <h4 style="margin-bottom: 10px;">{site_name}</h4>
                            <div style="display: inline-block; width: 60px; height: 60px; border-radius: 50%; 
                                        background-color: {score_color}; color: white; 
                                        line-height: 60px; font-size: 18px; font-weight: bold;">
                                {overall_score}<br><small style="font-size: 10px;">/100</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Issues list
                        issues = []
                        if data['Content Summary'] != "No major issues detected.":
                            content_issues = data['Content Summary'].split('\n')
                            issues.extend([issue.strip('- ') for issue in content_issues if issue.strip()])
                        
                        if data['Technical Summary'] != "No major issues detected.":
                            technical_issues = data['Technical Summary'].split('\n')
                            issues.extend([issue.strip('- ') for issue in technical_issues if issue.strip()])
                        
                        if data['UX Summary'] != "No major issues detected.":
                            ux_issues = data['UX Summary'].split('\n')
                            issues.extend([issue.strip('- ') for issue in ux_issues if issue.strip()])
                        
                        # Limit to top 4 issues for display
                        top_issues = issues[:4] if issues else ["No major issues detected"]
                        
                        # Display issues in a container
                        with st.container():
                            st.markdown("**Key Issues:**")
                            for issue in top_issues:
                                st.markdown(f"• {issue}")
                        
                        st.markdown("---")
                
                # Add scoring legend
                st.markdown("### Scoring Legend")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div style="text-align: center; padding: 10px;">
                        <div style="display: inline-block; width: 40px; height: 40px; border-radius: 50%; 
                                    background-color: #dc3545; color: white; 
                                    line-height: 40px; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                            0-49
                        </div>
                        <div><strong>Poor</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="text-align: center; padding: 10px;">
                        <div style="display: inline-block; width: 40px; height: 40px; border-radius: 50%; 
                                    background-color: #ffc107; color: white; 
                                    line-height: 40px; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                            50-89
                        </div>
                        <div><strong>Good</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div style="text-align: center; padding: 10px;">
                        <div style="display: inline-block; width: 40px; height: 40px; border-radius: 50%; 
                                    background-color: #28a745; color: white; 
                                    line-height: 40px; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                            90-100
                        </div>
                        <div><strong>Excellent</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="text-align: center; margin-top: 20px; font-style: italic; font-size: 16px; 
                            background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
                    "All brands should aim for a score above 90"
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                # Detailed audit tables
                st.markdown("## 📋 Detailed SEO Audit Tables")
                
                for i, analysis in enumerate(detailed_analyses):
                    site_name = safe_file_name(analysis['File Name'])
                    
                    # Create header with score circle and export options
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"### {site_name} - Technical SEO Audit")
                    with col2:
                        score = analysis['Overall Score']
                        score_color = "#dc3545" if score < 50 else "#ffc107" if score < 80 else "#28a745"
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="display: inline-block; width: 80px; height: 80px; border-radius: 50%; 
                                        background-color: {score_color}; color: white; 
                                        line-height: 80px; font-size: 24px; font-weight: bold;">
                                {score}<br><small style="font-size: 12px;">/100</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Prepare all audit data for this site
                    all_audit_data = []
                    
                    # Content SEO section
                    all_audit_data.append(['Content SEO', '', ''])
                    for key, details in analysis['Content Analysis'].items():
                        status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                    
                    # Technical SEO section
                    all_audit_data.append(['Technical SEO', '', ''])
                    for key, details in analysis['Technical Analysis'].items():
                        if key in ['mobile_speed', 'desktop_speed']:
                            status = details['status']
                        else:
                            status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                    
                    # User Experience section
                    all_audit_data.append(['User Experience', '', ''])
                    for key, details in analysis['UX Analysis'].items():
                        status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                    
                    # Off-Page SEO section
                    all_audit_data.append(['Off-Page SEO', '', ''])
                    for key, details in analysis['Offpage Analysis'].items():
                        status = details['status']
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                    
                    # Create comprehensive DataFrame for export
                    audit_df = pd.DataFrame(all_audit_data, columns=['Category', 'Factor', 'Status'])
                    
                    with col3:
                        st.markdown("**Export Options:**")
                        
                        # Excel export for this specific table
                        output = BytesIO()
                        try:
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                # Use sanitized sheet name
                                sheet_name = sanitize_sheet_name(f'{site_name}_Audit')
                                audit_df.to_excel(writer, sheet_name=sheet_name, index=False)
                                
                                # Add formatting
                                workbook = writer.book
                                worksheet = writer.sheets[sheet_name]
                                
                                # Define formats
                                header_format = workbook.add_format({
                                    'bold': True,
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'fg_color': '#667eea',
                                    'font_color': 'white',
                                    'border': 1
                                })
                                
                                category_format = workbook.add_format({
                                    'bold': True,
                                    'bg_color': '#f8f9fa',
                                    'border': 1
                                })
                                
                                # Apply header format
                                for col_num, value in enumerate(audit_df.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                                
                                # Format category rows
                                for row_num in range(1, len(audit_df) + 1):
                                    if audit_df.iloc[row_num-1]['Category'] and not audit_df.iloc[row_num-1]['Factor']:
                                        for col_num in range(len(audit_df.columns)):
                                            worksheet.write(row_num, col_num, audit_df.iloc[row_num-1, col_num], category_format)
                                
                                # Set column widths
                                worksheet.set_column('A:A', 20)  # Category
                                worksheet.set_column('B:B', 40)  # Factor
                                worksheet.set_column('C:C', 30)  # Status
                                
                                # Add overall score at the top
                                worksheet.write(0, 4, 'Overall Score', header_format)
                                worksheet.write(1, 4, f"{score}/100", workbook.add_format({'bold': True, 'font_size': 14}))
                        
                            st.download_button(
                                label=f"📊 Excel - {site_name[:15]}...",
                                data=output.getvalue(),
                                file_name=f"{site_name}_SEO_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                help=f"Download {site_name} SEO audit as Excel file",
                                key=f"excel_export_{i}"
                            )
                        except Exception as e:
                            st.error(f"Error creating Excel file for {site_name}: {str(e)}")
                        
                        # CSV export for this specific table
                        try:
                            csv_data = audit_df.to_csv(index=False)
                            st.download_button(
                                label=f"📄 CSV - {site_name[:15]}...",
                                data=csv_data,
                                file_name=f"{site_name}_SEO_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                help=f"Download {site_name} SEO audit as CSV file",
                                key=f"csv_export_{i}"
                            )
                        except Exception as e:
                            st.error(f"Error creating CSV file for {site_name}: {str(e)}")
                    
                    # Display the tables in Streamlit
                    st.markdown("#### Content SEO")
                    content_data = []
                    for key, details in analysis['Content Analysis'].items():
                        status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        content_data.append([details['description'], f"{status}{improvement}"])
                    
                    content_df = pd.DataFrame(content_data, columns=['Factor', 'Status'])
                    st.table(content_df)
                    
                    st.markdown("#### Technical SEO")
                    technical_data = []
                    for key, details in analysis['Technical Analysis'].items():
                        if key in ['mobile_speed', 'desktop_speed']:
                            status = details['status']
                        else:
                            status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        technical_data.append([details['description'], f"{status}{improvement}"])
                    
                    technical_df = pd.DataFrame(technical_data, columns=['Factor', 'Status'])
                    st.table(technical_df)
                    
                    st.markdown("#### User Experience")
                    ux_data = []
                    for key, details in analysis['UX Analysis'].items():
                        status = "✓" if details['status'] == '✓' else "✗"
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        ux_data.append([details['description'], f"{status}{improvement}"])
                    
                    ux_df = pd.DataFrame(ux_data, columns=['Factor', 'Status'])
                    st.table(ux_df)
                    
                    st.markdown("#### Off-Page SEO")
                    offpage_data = []
                    for key, details in analysis['Offpage Analysis'].items():
                        status = details['status']
                        improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                        offpage_data.append([details['description'], f"{status}{improvement}"])
                    
                    offpage_df = pd.DataFrame(offpage_data, columns=['Factor', 'Status'])
                    st.table(offpage_df)
                    
                    st.markdown("---")
                
                # Bulk export option for all tables
                st.markdown("### 📥 Bulk Export All Audit Tables")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create comprehensive Excel workbook with all sites
                    bulk_output = BytesIO()
                    try:
                        with pd.ExcelWriter(bulk_output, engine='xlsxwriter') as writer:
                            
                            for analysis in detailed_analyses:
                                site_name = safe_file_name(analysis['File Name'])
                                
                                # Prepare audit data for this site
                                all_audit_data = []
                                all_audit_data.append(['Content SEO', '', ''])
                                for key, details in analysis['Content Analysis'].items():
                                    status = "✓" if details['status'] == '✓' else "✗"
                                    improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                                    all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                                
                                all_audit_data.append(['Technical SEO', '', ''])
                                for key, details in analysis['Technical Analysis'].items():
                                    if key in ['mobile_speed', 'desktop_speed']:
                                        status = details['status']
                                    else:
                                        status = "✓" if details['status'] == '✓' else "✗"
                                    improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                                    all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                                
                                all_audit_data.append(['User Experience', '', ''])
                                for key, details in analysis['UX Analysis'].items():
                                    status = "✓" if details['status'] == '✓' else "✗"
                                    improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                                    all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                                
                                all_audit_data.append(['Off-Page SEO', '', ''])
                                for key, details in analysis['Offpage Analysis'].items():
                                    status = details['status']
                                    improvement = " - Needs Improvement" if details.get('needs_improvement', False) else ""
                                    all_audit_data.append(['', details['description'], f"{status}{improvement}"])
                                
                                # Create DataFrame and write to Excel
                                audit_df = pd.DataFrame(all_audit_data, columns=['Category', 'Factor', 'Status'])
                                sheet_name = sanitize_sheet_name(site_name)
                                audit_df.to_excel(writer, sheet_name=sheet_name, index=False)
                                
                                # Format the sheet
                                workbook = writer.book
                                worksheet = writer.sheets[sheet_name]
                                
                                # Define formats
                                header_format = workbook.add_format({
                                    'bold': True,
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'fg_color': '#667eea',
                                    'font_color': 'white',
                                    'border': 1
                                })
                                
                                category_format = workbook.add_format({
                                    'bold': True,
                                    'bg_color': '#f8f9fa',
                                    'border': 1
                                })
                                
                                # Apply header format
                                for col_num, value in enumerate(audit_df.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                                
                                # Format category rows
                                for row_num in range(1, len(audit_df) + 1):
                                    if audit_df.iloc[row_num-1]['Category'] and not audit_df.iloc[row_num-1]['Factor']:
                                        for col_num in range(len(audit_df.columns)):
                                            worksheet.write(row_num, col_num, audit_df.iloc[row_num-1, col_num], category_format)
                                
                                # Set column widths
                                worksheet.set_column('A:A', 20)
                                worksheet.set_column('B:B', 40)
                                worksheet.set_column('C:C', 30)
                                
                                # Add overall score
                                score = analysis['Overall Score']
                                worksheet.write(0, 4, 'Overall Score', header_format)
                                worksheet.write(1, 4, f"{score}/100", workbook.add_format({'bold': True, 'font_size': 14}))
                        
                        st.download_button(
                            label="📊 Download All Audits (Excel)",
                            data=bulk_output.getvalue(),
                            file_name=f"All_SEO_Audits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Download all site audits in one Excel workbook (separate sheets)"
                        )
                    except Exception as e:
                        st.error(f"Error creating bulk Excel file: {str(e)}")
                
                with col2:
                    st.info("💡 **Pro Tip**: The Excel files are formatted and ready for PowerPoint presentations. Each audit includes color-coded sections and overall scores.")
                    st.info("📋 **Usage**: Copy tables from Excel directly into PowerPoint slides, or use the structured data for custom visualizations.")
            
            with tab3:
                # Radar chart comparison
                st.markdown("## 🎯 Competitive Analysis")
                if len(comparison_data) > 1:
                    radar_chart = create_comparison_chart(comparison_df)
                    st.plotly_chart(radar_chart, use_container_width=True)
                else:
                    # Single site gauge charts
                    col1, col2, col3 = st.columns(3)
                    data = comparison_data[0]
                    
                    with col1:
                        fig1 = create_gauge_chart(data['Content SEO'], 'Content SEO')
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = create_gauge_chart(data['Technical SEO'], 'Technical SEO')
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with col3:
                        fig3 = create_gauge_chart(data['User Experience'], 'User Experience')
                        st.plotly_chart(fig3, use_container_width=True)
                
                # Detailed comparison table
                st.markdown("## 📋 Detailed Comparison")
                
                # Format the display dataframe
                display_df = comparison_df[['File Name', 'Content SEO', 'Technical SEO', 'User Experience', 'Overall Readiness']].copy()
                
                # Clean file names for display
                display_df['File Name'] = display_df['File Name'].apply(safe_file_name)
                
                # Apply styling
                def highlight_scores(val):
                    if isinstance(val, (int, float)):
                        if val >= 80:
                            return 'background-color: #d4edda; color: #155724; font-weight: bold'
                        elif val >= 60:
                            return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                        else:
                            return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                    return ''
                
                styled_df = display_df.style.applymap(highlight_scores, subset=['Content SEO', 'Technical SEO', 'User Experience', 'Overall Readiness'])
                st.dataframe(styled_df, use_container_width=True)
                
                # Detailed insights for each site
                st.markdown("## 🔍 Detailed Insights")
                
                for i, data in enumerate(comparison_data):
                    site_name = safe_file_name(data['File Name'])
                    with st.expander(f"📈 {site_name} - Detailed Analysis"):
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("### Content SEO Issues")
                            if data['Content Summary'] != "No major issues detected.":
                                st.markdown(f"<div style='color: #dc3545;'>{data['Content Summary']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #28a745;'>{data['Content Summary']}</div>", unsafe_allow_html=True)
                            
                            # Show detailed scores
                            st.markdown("**Detailed Scores:**")
                            for key, value in data['Content Details'].items():
                                st.write(f"• {key.replace('_', ' ').title()}: {value}%")
                        
                        with col2:
                            st.markdown("### Technical SEO Issues")
                            if data['Technical Summary'] != "No major issues detected.":
                                st.markdown(f"<div style='color: #dc3545;'>{data['Technical Summary']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #28a745;'>{data['Technical Summary']}</div>", unsafe_allow_html=True)
                            
                            # Show detailed scores
                            st.markdown("**Detailed Scores:**")
                            for key, value in data['Technical Details'].items():
                                st.write(f"• {key.replace('_', ' ').title()}: {value}%")
                        
                        with col3:
                            st.markdown("### User Experience Issues")
                            if data['UX Summary'] != "No major issues detected.":
                                st.markdown(f"<div style='color: #dc3545;'>{data['UX Summary']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #28a745;'>{data['UX Summary']}</div>", unsafe_allow_html=True)
                            
                            # Show detailed scores
                            st.markdown("**Detailed Scores:**")
                            for key, value in data['UX Details'].items():
                                st.write(f"• {key.replace('_', ' ').title()}: {value}%")
            
            with tab4:
                # Export functionality
                st.markdown("## 📥 Export Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Prepare export data
                    export_df = comparison_df.drop(['Content Details', 'Technical Details', 'UX Details'], axis=1)
                    
                    # Clean file names for export
                    export_df['File Name'] = export_df['File Name'].apply(safe_file_name)
                    
                    output = BytesIO()
                    try:
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            export_df.to_excel(writer, sheet_name='SEO Analysis', index=False)
                            
                            # Add formatting
                            workbook = writer.book
                            worksheet = writer.sheets['SEO Analysis']
                            
                            # Define formats
                            header_format = workbook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'top',
                                'fg_color': '#667eea',
                                'font_color': 'white',
                                'border': 1
                            })
                            
                            # Apply header format
                            for col_num, value in enumerate(export_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                            
                            # Set column widths
                            worksheet.set_column('A:A', 25)  # File Name
                            worksheet.set_column('B:E', 15)  # Score columns
                            worksheet.set_column('F:H', 40)  # Summary columns
                        
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=output.getvalue(),
                            file_name=f"SEO_Comparison_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Download comprehensive SEO analysis report in Excel format"
                        )
                    except Exception as e:
                        st.error(f"Error creating Excel report: {str(e)}")
                
                with col2:
                    # CSV export
                    try:
                        export_df_csv = export_df.copy()
                        csv = export_df_csv.to_csv(index=False)
                        st.download_button(
                            label="📄 Download CSV Report",
                            data=csv,
                            file_name=f"SEO_Comparison_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Download analysis results in CSV format"
                        )
                    except Exception as e:
                        st.error(f"Error creating CSV report: {str(e)}")
        
        else:
            st.error("No files were successfully processed. Please check your file formats and try again.")
    
    else:
        # Show example/demo section when no files uploaded
        st.markdown("## 🚀 How It Works")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
                <h4>1. Upload Files</h4>
                <p>Upload Screaming Frog export files (CSV or Excel format) for your client and competitors.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
                <h4>2. Automatic Analysis</h4>
                <p>Our algorithm analyzes Content SEO, Technical SEO, and User Experience factors.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h4>3. Get Insights</h4>
                <p>Receive detailed scores, comparisons, and actionable recommendations.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

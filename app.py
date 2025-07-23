import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

class SEOScorer:
    def __init__(self):
        self.weights = {
            'content_seo': 0.4,
            'technical_seo': 0.4,
            'user_experience': 0.2
        }
        self.recommendations_engine = AIRecommendationsEngine()

    def analyze_content_seo(self, df):
        scores = {}
        weaknesses = []

        title_score = 0
        if 'Title 1' in df.columns and 'Title 1 Length' in df.columns:
            valid_titles = df['Title 1'].notna()
            good_length = (df['Title 1 Length'] >= 30) & (df['Title 1 Length'] <= 60)
            title_score = ((valid_titles & good_length).mean() * 100)
            if title_score < 50:
                weaknesses.append("Short or missing meta titles.")
        scores['meta_title'] = round(title_score)

        desc_score = 0
        if 'Meta Description 1' in df.columns and 'Meta Description 1 Length' in df.columns:
            valid_desc = df['Meta Description 1'].notna()
            good_length = (df['Meta Description 1 Length'] >= 120) & (df['Meta Description 1 Length'] <= 160)
            desc_score = ((valid_desc & good_length).mean() * 100)
            if desc_score < 50:
                weaknesses.append("Short or missing meta descriptions.")
        scores['meta_description'] = round(desc_score)

        h1_score = 0
        if 'H1-1' in df.columns:
            h1_score = df['H1-1'].notna().mean() * 100
            if h1_score < 50:
                weaknesses.append("Missing or poorly optimized H1 tags.")
        scores['h1_tags'] = round(h1_score)

        internal_linking_score = 0
        if 'Inlinks' in df.columns and 'Unique Inlinks' in df.columns:
            has_inlinks = df['Inlinks'] > 0
            has_unique_inlinks = df['Unique Inlinks'] > 0
            internal_linking_score = ((has_inlinks & has_unique_inlinks).mean() * 100)
            if internal_linking_score < 50:
                weaknesses.append("Insufficient internal linking.")
        scores['internal_linking'] = round(internal_linking_score)

        content_quality_score = 0
        if 'Word Count' in df.columns and 'Flesch Reading Ease Score' in df.columns:
            good_length = df['Word Count'] >= 300
            readable = df['Flesch Reading Ease Score'] >= 60
            content_quality_score = ((good_length & readable).mean() * 100)
            if content_quality_score < 50:
                weaknesses.append("Low content quality or poor readability.")
        scores['content_quality'] = round(content_quality_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_technical_seo(self, df):
        scores = {}
        weaknesses = []

        response_score = 0
        if 'Response Time' in df.columns:
            good_response = df['Response Time'] <= 1.0
            response_score = good_response.mean() * 100
            if response_score < 50:
                weaknesses.append("Slow response times.")
        scores['response_time'] = round(response_score)

        status_score = 0
        if 'Status Code' in df.columns:
            good_status = df['Status Code'] == 200
            status_score = good_status.mean() * 100
            if status_score < 70:
                weaknesses.append("Issues with HTTP status codes.")
        scores['status_codes'] = round(status_score)

        index_score = 0
        if 'Indexability' in df.columns:
            indexable = df['Indexability'] == 'Indexable'
            index_score = indexable.mean() * 100
            if index_score < 70:
                weaknesses.append("Pages not indexable.")
        scores['indexability'] = round(index_score)

        canonical_score = 0
        if 'Canonical Link Element 1' in df.columns:
            valid_canonical = df['Canonical Link Element 1'].notna()
            canonical_score = valid_canonical.mean() * 100
            if canonical_score < 70:
                weaknesses.append("Improper or missing canonical tags.")
        scores['canonical_tags'] = round(canonical_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

    def analyze_user_experience(self, df):
        scores = {}
        weaknesses = []

        mobile_score = 0
        if 'Mobile Alternate Link' in df.columns:
            mobile_score = df['Mobile Alternate Link'].notna().mean() * 100
            if mobile_score < 50:
                weaknesses.append("Pages not mobile-friendly.")
        scores['mobile_friendly'] = round(mobile_score)

        lcp_score = 0
        if 'Largest Contentful Paint Time (ms)' in df.columns:
            good_lcp = df['Largest Contentful Paint Time (ms)'] <= 2500
            lcp_score = good_lcp.mean() * 100
            if lcp_score < 50:
                weaknesses.append("Slow LCP times.")
        scores['largest_contentful_paint'] = round(lcp_score)

        cls_score = 0
        if 'Cumulative Layout Shift' in df.columns:
            good_cls = df['Cumulative Layout Shift'] <= 0.1
            cls_score = good_cls.mean() * 100
            if cls_score < 50:
                weaknesses.append("High CLS values.")
        scores['cumulative_layout_shift'] = round(cls_score)

        return round(np.mean(list(scores.values()))), scores, weaknesses

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

class AIRecommendationsEngine:
    def __init__(self):
        self.impact_weights = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'informational': 1
        }
        
        self.effort_levels = {
            'quick_win': 1,    # < 1 hour
            'easy': 2,         # 1-4 hours
            'moderate': 3,     # 1-2 days
            'complex': 4,      # 1 week
            'major': 5         # > 1 week
        }
    
    def generate_recommendations(self, scores, weaknesses, site_type="general", df=None):
        """Generate AI-powered recommendations based on analysis results"""
        recommendations = []
        
        # Content SEO Recommendations
        content_recs = self._analyze_content_issues(scores.get('content_details', {}), weaknesses.get('content', []), df)
        recommendations.extend(content_recs)
        
        # Technical SEO Recommendations
        technical_recs = self._analyze_technical_issues(scores.get('technical_details', {}), weaknesses.get('technical', []), df)
        recommendations.extend(technical_recs)
        
        # UX Recommendations
        ux_recs = self._analyze_ux_issues(scores.get('ux_details', {}), weaknesses.get('ux', []), df)
        recommendations.extend(ux_recs)
        
        # Sort by priority score (impact/effort ratio)
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return recommendations
    
    def _analyze_content_issues(self, content_scores, content_weaknesses, df):
        recommendations = []
        
        # Meta Title Issues
        if content_scores.get('meta_title', 0) < 70:
            impact = 'critical' if content_scores.get('meta_title', 0) < 40 else 'high'
            recommendations.append({
                'category': 'Content SEO',
                'issue': 'Meta Title Optimization',
                'description': 'Many pages have missing or poorly optimized meta titles',
                'recommendation': 'Create unique, descriptive titles (30-60 characters) for each page that include primary keywords naturally',
                'impact': impact,
                'effort': 'moderate',
                'priority_score': self._calculate_priority(impact, 'moderate'),
                'steps': [
                    'Audit all pages with missing or short titles',
                    'Research primary keywords for each page',
                    'Write compelling titles that include keywords naturally',
                    'Ensure titles are between 30-60 characters',
                    'Test titles for click-through rate improvements'
                ],
                'tools_needed': ['Screaming Frog', 'Google Search Console', 'Keyword research tool'],
                'estimated_time': '2-4 hours per 100 pages',
                'expected_impact': '+15-25% improvement in CTR from search results'
            })
        
        # Meta Description Issues
        if content_scores.get('meta_description', 0) < 70:
            impact = 'high' if content_scores.get('meta_description', 0) < 40 else 'medium'
            recommendations.append({
                'category': 'Content SEO',
                'issue': 'Meta Description Enhancement',
                'description': 'Meta descriptions are missing or not optimized for click-through rates',
                'recommendation': 'Write compelling meta descriptions (120-160 characters) that summarize page content and include a call-to-action',
                'impact': impact,
                'effort': 'easy',
                'priority_score': self._calculate_priority(impact, 'easy'),
                'steps': [
                    'Identify pages with missing/poor meta descriptions',
                    'Write unique descriptions for each page',
                    'Include primary keywords naturally',
                    'Add compelling calls-to-action',
                    'Keep within 120-160 character limit'
                ],
                'tools_needed': ['CMS/Website editor', 'SERP preview tool'],
                'estimated_time': '1-2 hours per 100 pages',
                'expected_impact': '+10-20% improvement in CTR from search results'
            })
        
        # H1 Tag Issues
        if content_scores.get('h1_tags', 0) < 70:
            recommendations.append({
                'category': 'Content SEO',
                'issue': 'H1 Tag Optimization',
                'description': 'Pages are missing H1 tags or have poorly structured headings',
                'recommendation': 'Ensure every page has a unique, descriptive H1 tag that includes the primary keyword',
                'impact': 'medium',
                'effort': 'easy',
                'priority_score': self._calculate_priority('medium', 'easy'),
                'steps': [
                    'Audit pages missing H1 tags',
                    'Create unique H1 for each page',
                    'Include primary keyword in H1',
                    'Ensure proper heading hierarchy (H1 > H2 > H3)'
                ],
                'tools_needed': ['Website editor', 'SEO crawler'],
                'estimated_time': '30 minutes per 100 pages',
                'expected_impact': '+5-10% improvement in page relevance scores'
            })
        
        # Internal Linking Issues
        if content_scores.get('internal_linking', 0) < 60:
            recommendations.append({
                'category': 'Content SEO',
                'issue': 'Internal Linking Strategy',
                'description': 'Poor internal linking structure affecting page authority distribution',
                'recommendation': 'Implement strategic internal linking to distribute page authority and improve navigation',
                'impact': 'high',
                'effort': 'moderate',
                'priority_score': self._calculate_priority('high', 'moderate'),
                'steps': [
                    'Map out site architecture and key pages',
                    'Identify high-authority pages that can pass link equity',
                    'Create contextual internal links with descriptive anchor text',
                    'Link to important pages from multiple sources',
                    'Monitor internal link distribution'
                ],
                'tools_needed': ['Site crawler', 'Internal link analysis tool'],
                'estimated_time': '4-8 hours for initial setup',
                'expected_impact': '+10-20% improvement in page rankings'
            })
        
        # Content Quality Issues
        if content_scores.get('content_quality', 0) < 60:
            recommendations.append({
                'category': 'Content SEO',
                'issue': 'Content Quality Enhancement',
                'description': 'Content is too short or has poor readability scores',
                'recommendation': 'Improve content depth and readability to better serve user intent',
                'impact': 'high',
                'effort': 'complex',
                'priority_score': self._calculate_priority('high', 'complex'),
                'steps': [
                    'Identify pages with thin content (<300 words)',
                    'Research user intent and competitor content',
                    'Expand content with valuable, relevant information',
                    'Improve readability with shorter sentences and paragraphs',
                    'Add relevant images, lists, and formatting'
                ],
                'tools_needed': ['Content research tools', 'Readability checker', 'Competitor analysis'],
                'estimated_time': '2-4 hours per page',
                'expected_impact': '+20-40% improvement in user engagement and rankings'
            })
        
        return recommendations
    
    def _analyze_technical_issues(self, technical_scores, technical_weaknesses, df):
        recommendations = []
        
        # Response Time Issues
        if technical_scores.get('response_time', 0) < 70:
            impact = 'critical' if technical_scores.get('response_time', 0) < 40 else 'high'
            recommendations.append({
                'category': 'Technical SEO',
                'issue': 'Page Speed Optimization',
                'description': 'Slow server response times affecting user experience and rankings',
                'recommendation': 'Optimize server performance and implement caching strategies',
                'impact': impact,
                'effort': 'complex',
                'priority_score': self._calculate_priority(impact, 'complex'),
                'steps': [
                    'Analyze server performance metrics',
                    'Implement browser and server-side caching',
                    'Optimize database queries',
                    'Use Content Delivery Network (CDN)',
                    'Compress images and minify CSS/JS',
                    'Consider upgrading hosting plan'
                ],
                'tools_needed': ['PageSpeed Insights', 'GTmetrix', 'Web hosting admin'],
                'estimated_time': '1-2 weeks for comprehensive optimization',
                'expected_impact': '+15-30% improvement in user experience and rankings'
            })
        
        # Status Code Issues
        if technical_scores.get('status_codes', 0) < 80:
            recommendations.append({
                'category': 'Technical SEO',
                'issue': 'HTTP Status Code Cleanup',
                'description': 'Multiple pages returning error status codes (404, 500, etc.)',
                'recommendation': 'Fix or redirect pages with error status codes to improve crawl efficiency',
                'impact': 'high',
                'effort': 'moderate',
                'priority_score': self._calculate_priority('high', 'moderate'),
                'steps': [
                    'Identify all pages with 4xx and 5xx errors',
                    'Determine if pages should be fixed or redirected',
                    'Implement 301 redirects for moved content',
                    'Fix broken internal links',
                    'Update XML sitemap to remove error pages'
                ],
                'tools_needed': ['Crawling tool', 'Server access', 'Redirect manager'],
                'estimated_time': '4-8 hours depending on error count',
                'expected_impact': '+10-15% improvement in crawl efficiency'
            })
        
        # Indexability Issues
        if technical_scores.get('indexability', 0) < 80:
            recommendations.append({
                'category': 'Technical SEO',
                'issue': 'Indexability Optimization',
                'description': 'Pages are blocked from search engine indexing',
                'recommendation': 'Review and fix indexability issues to ensure important pages can be found',
                'impact': 'critical',
                'effort': 'moderate',
                'priority_score': self._calculate_priority('critical', 'moderate'),
                'steps': [
                    'Review robots.txt file for blocking rules',
                    'Check meta robots tags on important pages',
                    'Ensure XML sitemap includes indexable pages',
                    'Remove noindex tags from important content',
                    'Submit updated sitemap to search engines'
                ],
                'tools_needed': ['Robots.txt editor', 'XML sitemap generator', 'Search Console'],
                'estimated_time': '2-4 hours for audit and fixes',
                'expected_impact': '+20-40% increase in indexed pages'
            })
        
        # Canonical Tag Issues
        if technical_scores.get('canonical_tags', 0) < 70:
            recommendations.append({
                'category': 'Technical SEO',
                'issue': 'Canonical Tag Implementation',
                'description': 'Missing or incorrect canonical tags causing duplicate content issues',
                'recommendation': 'Implement proper canonical tags to consolidate page authority and avoid duplicate content penalties',
                'impact': 'medium',
                'effort': 'moderate',
                'priority_score': self._calculate_priority('medium', 'moderate'),
                'steps': [
                    'Identify pages with missing canonical tags',
                    'Find duplicate or near-duplicate content',
                    'Implement self-referencing canonicals on unique pages',
                    'Point duplicate pages to preferred versions',
                    'Test canonical implementation'
                ],
                'tools_needed': ['SEO crawler', 'Duplicate content checker', 'Website editor'],
                'estimated_time': '3-6 hours for implementation',
                'expected_impact': '+5-15% improvement in page authority consolidation'
            })
        
        return recommendations
    
    def _analyze_ux_issues(self, ux_scores, ux_weaknesses, df):
        recommendations = []
        
        # Mobile Friendliness Issues
        if ux_scores.get('mobile_friendly', 0) < 70:
            recommendations.append({
                'category': 'User Experience',
                'issue': 'Mobile Optimization',
                'description': 'Website is not optimized for mobile devices',
                'recommendation': 'Implement responsive design and mobile-first optimization',
                'impact': 'critical',
                'effort': 'major',
                'priority_score': self._calculate_priority('critical', 'major'),
                'steps': [
                    'Audit mobile user experience',
                    'Implement responsive CSS framework',
                    'Optimize touch targets and navigation',
                    'Test on multiple mobile devices',
                    'Optimize mobile page speed'
                ],
                'tools_needed': ['Mobile testing tools', 'Responsive design framework', 'Device testing'],
                'estimated_time': '2-4 weeks for full mobile optimization',
                'expected_impact': '+25-50% improvement in mobile user engagement'
            })
        
        # Core Web Vitals Issues
        if ux_scores.get('largest_contentful_paint', 0) < 70:
            recommendations.append({
                'category': 'User Experience',
                'issue': 'Core Web Vitals Optimization',
                'description': 'Poor Core Web Vitals scores affecting user experience and rankings',
                'recommendation': 'Optimize Largest Contentful Paint, First Input Delay, and Cumulative Layout Shift',
                'impact': 'high',
                'effort': 'complex',
                'priority_score': self._calculate_priority('high', 'complex'),
                'steps': [
                    'Measure current Core Web Vitals performance',
                    'Optimize LCP by improving server response times',
                    'Reduce FID by optimizing JavaScript execution',
                    'Fix CLS by setting image and video dimensions',
                    'Monitor improvements with real user data'
                ],
                'tools_needed': ['PageSpeed Insights', 'Web Vitals extension', 'Performance monitoring'],
                'estimated_time': '1-2 weeks for comprehensive optimization',
                'expected_impact': '+15-25% improvement in user experience metrics'
            })
        
        return recommendations
    
    def _calculate_priority(self, impact, effort):
        """Calculate priority score based on impact vs effort"""
        impact_score = self.impact_weights.get(impact, 3)
        effort_score = self.effort_levels.get(effort, 3)
        
        # Higher impact and lower effort = higher priority
        priority_score = (impact_score * 2) / effort_score
        return round(priority_score, 2)
    
    def get_priority_label(self, priority_score):
        """Convert priority score to human-readable label"""
        if priority_score >= 4:
            return "🔴 Critical Priority"
        elif priority_score >= 3:
            return "🟠 High Priority"
        elif priority_score >= 2:
            return "🟡 Medium Priority"
        else:
            return "🟢 Low Priority"
    
    def generate_executive_summary(self, recommendations, overall_score):
        """Generate an executive summary of recommendations"""
        critical_issues = len([r for r in recommendations if r['priority_score'] >= 4])
        high_priority = len([r for r in recommendations if 3 <= r['priority_score'] < 4])
        
        summary = {
            'overall_health': 'Good' if overall_score >= 70 else 'Needs Improvement' if overall_score >= 50 else 'Poor',
            'critical_issues': critical_issues,
            'high_priority_issues': high_priority,
            'quick_wins': len([r for r in recommendations if r['effort'] in ['quick_win', 'easy']]),
            'estimated_improvement': f"+{min(30, len(recommendations) * 3)}% potential ranking improvement",
            'top_recommendation': recommendations[0] if recommendations else None
        }
        
        return summary

def create_score_visual(score, title):
    """Create a visual score representation using progress bars"""
    color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
    
    return f"""
    <div style="text-align: center; margin: 1rem 0;">
        <h4 style="margin-bottom: 0.5rem;">{title}</h4>
        <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; margin: 0.5rem 0;">
            <div style="background-color: {color}; height: 100%; width: {score}%; border-radius: 10px; transition: width 0.3s ease;"></div>
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{score}%</div>
    </div>
    """

def create_comparison_table_chart(comparison_df):
    """Create a bar chart comparison using Streamlit's native charting"""
    chart_data = comparison_df.set_index('File Name')[['Content SEO', 'Technical SEO', 'User Experience', 'Overall Readiness']]
    return chart_data

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
                content_score, content_details, content_weaknesses = scorer.analyze_content_seo(df)
                technical_score, technical_details, technical_weaknesses = scorer.analyze_technical_seo(df)
                ux_score, ux_details, ux_weaknesses = scorer.analyze_user_experience(df)
                overall_score = scorer.calculate_overall_score(content_score, technical_score, ux_score)
                
                # Generate AI recommendations
                all_scores = {
                    'content_details': content_details,
                    'technical_details': technical_details,
                    'ux_details': ux_details
                }
                all_weaknesses = {
                    'content': content_weaknesses,
                    'technical': technical_weaknesses,
                    'ux': ux_weaknesses
                }
                
                recommendations = scorer.recommendations_engine.generate_recommendations(
                    all_scores, all_weaknesses, "general", df
                )
                
                executive_summary = scorer.recommendations_engine.generate_executive_summary(
                    recommendations, overall_score
                )
                
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
                    "UX Details": ux_details,
                    "AI Recommendations": recommendations,
                    "Executive Summary": executive_summary
                })
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
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
            
            # AI-Powered Executive Summary
            st.markdown("## 🤖 AI-Powered Executive Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📋 Overall Assessment")
                for i, data in enumerate(comparison_data):
                    exec_summary = data['Executive Summary']
                    site_name = data['File Name'].replace('.csv', '').replace('.xlsx', '')
                    
                    with st.expander(f"📊 {site_name} - Executive Summary", expanded=i==0):
                        health_color = "#28a745" if exec_summary['overall_health'] == 'Good' else "#ffc107" if exec_summary['overall_health'] == 'Needs Improvement' else "#dc3545"
                        
                        st.markdown(f"""
                        <div style="background: {health_color}20; padding: 1rem; border-radius: 8px; border-left: 4px solid {health_color};">
                            <h4 style="color: {health_color}; margin: 0;">Site Health: {exec_summary['overall_health']}</h4>
                            <p style="margin: 0.5rem 0;"><strong>🔴 Critical Issues:</strong> {exec_summary['critical_issues']}</p>
                            <p style="margin: 0.5rem 0;"><strong>🟠 High Priority Issues:</strong> {exec_summary['high_priority_issues']}</p>
                            <p style="margin: 0.5rem 0;"><strong>⚡ Quick Wins Available:</strong> {exec_summary['quick_wins']}</p>
                            <p style="margin: 0.5rem 0;"><strong>📈 Potential Improvement:</strong> {exec_summary['estimated_improvement']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if exec_summary['top_recommendation']:
                            top_rec = exec_summary['top_recommendation']
                            st.markdown("**🎯 Top Priority Action:**")
                            st.info(f"{top_rec['issue']}: {top_rec['recommendation']}")
            
            with col2:
                st.markdown("### 🏆 Competitive Ranking")
                ranking_data = []
                for data in comparison_data:
                    exec_summary = data['Executive Summary']
                    ranking_data.append({
                        'Site': data['File Name'].replace('.csv', '').replace('.xlsx', ''),
                        'Overall Score': data['Overall Readiness'],
                        'Critical Issues': exec_summary['critical_issues'],
                        'Quick Wins': exec_summary['quick_wins'],
                        'Health Status': exec_summary['overall_health']
                    })
                
                ranking_df = pd.DataFrame(ranking_data).sort_values('Overall Score', ascending=False)
                ranking_df['Rank'] = range(1, len(ranking_df) + 1)
                ranking_df = ranking_df[['Rank', 'Site', 'Overall Score', 'Health Status', 'Critical Issues', 'Quick Wins']]
                
                st.dataframe(ranking_df, use_container_width=True, hide_index=True)
            
            # AI Recommendations Section
            st.markdown("## 🎯 AI-Powered Recommendations")
            
            for i, data in enumerate(comparison_data):
                site_name = data['File Name'].replace('.csv', '').replace('.xlsx', '')
                recommendations = data['AI Recommendations']
                
                with st.expander(f"🚀 {site_name} - Smart Action Plan ({len(recommendations)} recommendations)", expanded=i==0):
                    if recommendations:
                        # Priority filter
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            priority_filter = st.selectbox(
                                "Filter by Priority",
                                ["All", "Critical Priority", "High Priority", "Medium Priority", "Low Priority"],
                                key=f"priority_filter_{i}"
                            )
                        
                        with col2:
                            category_filter = st.selectbox(
                                "Filter by Category",
                                ["All", "Content SEO", "Technical SEO", "User Experience"],
                                key=f"category_filter_{i}"
                            )
                        
                        with col3:
                            effort_filter = st.selectbox(
                                "Filter by Effort",
                                ["All", "Quick Win", "Easy", "Moderate", "Complex", "Major"],
                                key=f"effort_filter_{i}"
                            )
                        
                        # Filter recommendations
                        filtered_recs = recommendations.copy()
                        
                        if priority_filter != "All":
                            if priority_filter == "Critical Priority":
                                filtered_recs = [r for r in filtered_recs if r['priority_score'] >= 4]
                            elif priority_filter == "High Priority":
                                filtered_recs = [r for r in filtered_recs if 3 <= r['priority_score'] < 4]
                            elif priority_filter == "Medium Priority":
                                filtered_recs = [r for r in filtered_recs if 2 <= r['priority_score'] < 3]
                            elif priority_filter == "Low Priority":
                                filtered_recs = [r for r in filtered_recs if r['priority_score'] < 2]
                        
                        if category_filter != "All":
                            filtered_recs = [r for r in filtered_recs if r['category'] == category_filter]
                        
                        if effort_filter != "All":
                            effort_map = {"Quick Win": "quick_win", "Easy": "easy", "Moderate": "moderate", "Complex": "complex", "Major": "major"}
                            filtered_recs = [r for r in filtered_recs if r['effort'] == effort_map.get(effort_filter, effort_filter.lower())]
                        
                        # Display recommendations
                        for j, rec in enumerate(filtered_recs[:10]):  # Show top 10
                            priority_label = "🔴 Critical" if rec['priority_score'] >= 4 else "🟠 High" if rec['priority_score'] >= 3 else "🟡 Medium" if rec['priority_score'] >= 2 else "🟢 Low"
                            
                            effort_emoji = {"quick_win": "⚡", "easy": "🟢", "moderate": "🟡", "complex": "🟠", "major": "🔴"}
                            effort_display = f"{effort_emoji.get(rec['effort'], '⚪')} {rec['effort'].replace('_', ' ').title()}"
                            
                            with st.container():
                                st.markdown(f"""
                                <div style="background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                                        <h4 style="margin: 0; color: #333;">{rec['issue']}</h4>
                                        <div style="display: flex; gap: 1rem;">
                                            <span style="background: #e3f2fd; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">{priority_label}</span>
                                            <span style="background: #f3e5f5; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">{effort_display}</span>
                                            <span style="background: #e8f5e8; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">{rec['category']}</span>
                                        </div>
                                    </div>
                                    <p style="color: #666; margin-bottom: 1rem;"><strong>Issue:</strong> {rec['description']}</p>
                                    <p style="color: #333; margin-bottom: 1rem;"><strong>💡 Recommendation:</strong> {rec['recommendation']}</p>
                                    <p style="color: #28a745; margin-bottom: 0;"><strong>📈 Expected Impact:</strong> {rec['expected_impact']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Expandable detailed steps
                                with st.expander(f"📋 Detailed Action Steps - {rec['issue']}", expanded=False):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("**🎯 Step-by-Step Guide:**")
                                        for step_num, step in enumerate(rec['steps'], 1):
                                            st.markdown(f"{step_num}. {step}")
                                        
                                        st.markdown(f"**⏱️ Estimated Time:** {rec['estimated_time']}")
                                    
                                    with col2:
                                        st.markdown("**🛠️ Tools Needed:**")
                                        for tool in rec['tools_needed']:
                                            st.markdown(f"• {tool}")
                        
                        if len(filtered_recs) == 0:
                            st.info("No recommendations match the selected filters.")
                        elif len(recommendations) > 10:
                            st.info(f"Showing top 10 of {len(filtered_recs)} filtered recommendations.")
                    
                    else:
                        st.success("🎉 Excellent! No major issues detected. Your site is well-optimized!")
            
            st.markdown("---")
            # Performance visualization
            st.markdown("## 🎯 Performance Visualization")
            if len(comparison_data) > 1:
                # Multi-site comparison using bar chart
                chart_data = create_comparison_table_chart(comparison_df)
                st.bar_chart(chart_data)
                
                # Show ranking
                st.markdown("### 🏆 Performance Ranking")
                ranking_df = comparison_df[['File Name', 'Overall Readiness']].sort_values('Overall Readiness', ascending=False)
                ranking_df['Rank'] = range(1, len(ranking_df) + 1)
                ranking_df = ranking_df[['Rank', 'File Name', 'Overall Readiness']]
                st.dataframe(ranking_df, use_container_width=True, hide_index=True)
                
            else:
                # Single site visualization with progress bars
                data = comparison_data[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(create_score_visual(data['Content SEO'], 'Content SEO'), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(create_score_visual(data['Technical SEO'], 'Technical SEO'), unsafe_allow_html=True)
                
                with col3:
                    st.markdown(create_score_visual(data['User Experience'], 'User Experience'), unsafe_allow_html=True)
                
                # Overall score prominently displayed
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 2rem 0;">
                    <h2 style="margin-bottom: 1rem;">Overall SEO Readiness</h2>
                    <div style="font-size: 4rem; font-weight: bold; margin-bottom: 0.5rem;">{data['Overall Readiness']}%</div>
                    <p style="font-size: 1.2rem; margin: 0;">
                        {'Excellent' if data['Overall Readiness'] >= 80 else 'Good' if data['Overall Readiness'] >= 60 else 'Needs Improvement'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed comparison table
            st.markdown("## 📋 Detailed Comparison")
            
            # Format the display dataframe
            display_df = comparison_df[['File Name', 'Content SEO', 'Technical SEO', 'User Experience', 'Overall Readiness']].copy()
            
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
                with st.expander(f"📈 {data['File Name']} - Detailed Analysis"):
                    
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
            
            # Export functionality
            st.markdown("## 📥 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Prepare export data with AI recommendations
                export_df = comparison_df.drop(['Content Details', 'Technical Details', 'UX Details', 'AI Recommendations', 'Executive Summary'], axis=1)
                
                # Create comprehensive Excel report with AI insights
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Main comparison sheet
                    export_df.to_excel(writer, sheet_name='SEO Comparison', index=False)
                    
                    # AI Recommendations sheet
                    recommendations_data = []
                    for data in comparison_data:
                        site_name = data['File Name'].replace('.csv', '').replace('.xlsx', '')
                        for rec in data['AI Recommendations']:
                            recommendations_data.append({
                                'Site': site_name,
                                'Priority Score': rec['priority_score'],
                                'Priority Level': scorer.recommendations_engine.get_priority_label(rec['priority_score']).replace('🔴 ', '').replace('🟠 ', '').replace('🟡 ', '').replace('🟢 ', ''),
                                'Category': rec['category'],
                                'Issue': rec['issue'],
                                'Description': rec['description'],
                                'Recommendation': rec['recommendation'],
                                'Impact': rec['impact'].title(),
                                'Effort': rec['effort'].replace('_', ' ').title(),
                                'Expected Impact': rec['expected_impact'],
                                'Estimated Time': rec['estimated_time'],
                                'Action Steps': ' | '.join(rec['steps']),
                                'Tools Needed': ', '.join(rec['tools_needed'])
                            })
                    
                    if recommendations_data:
                        recommendations_df = pd.DataFrame(recommendations_data)
                        recommendations_df = recommendations_df.sort_values(['Site', 'Priority Score'], ascending=[True, False])
                        recommendations_df.to_excel(writer, sheet_name='AI Recommendations', index=False)
                    
                    # Executive Summary sheet
                    exec_summary_data = []
                    for data in comparison_data:
                        site_name = data['File Name'].replace('.csv', '').replace('.xlsx', '')
                        exec_summary = data['Executive Summary']
                        exec_summary_data.append({
                            'Site': site_name,
                            'Overall Score': data['Overall Readiness'],
                            'Health Status': exec_summary['overall_health'],
                            'Critical Issues': exec_summary['critical_issues'],
                            'High Priority Issues': exec_summary['high_priority_issues'],
                            'Quick Wins Available': exec_summary['quick_wins'],
                            'Potential Improvement': exec_summary['estimated_improvement'],
                            'Top Recommendation': exec_summary['top_recommendation']['issue'] if exec_summary['top_recommendation'] else 'None'
                        })
                    
                    exec_summary_df = pd.DataFrame(exec_summary_data)
                    exec_summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
                    
                    # Format the workbook
                    workbook = writer.book
                    
                    # Define formats
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#667eea',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    priority_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top'
                    })
                    
                    # Apply formatting to all sheets
                    for sheet_name in writer.sheets:
                        worksheet = writer.sheets[sheet_name]
                        
                        # Get the dataframe for this sheet
                        if sheet_name == 'SEO Comparison':
                            df_to_format = export_df
                        elif sheet_name == 'AI Recommendations':
                            df_to_format = recommendations_df if recommendations_data else pd.DataFrame()
                        elif sheet_name == 'Executive Summary':
                            df_to_format = exec_summary_df
                        
                        if not df_to_format.empty:
                            # Apply header format
                            for col_num, value in enumerate(df_to_format.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                            
                            # Set column widths
                            if sheet_name == 'SEO Comparison':
                                worksheet.set_column('A:A', 25)  # File Name
                                worksheet.set_column('B:E', 15)  # Score columns
                                worksheet.set_column('F:H', 40)  # Summary columns
                            elif sheet_name == 'AI Recommendations':
                                worksheet.set_column('A:A', 20)  # Site
                                worksheet.set_column('B:B', 12)  # Priority Score
                                worksheet.set_column('C:C', 15)  # Priority Level
                                worksheet.set_column('D:D', 15)  # Category
                                worksheet.set_column('E:E', 25)  # Issue
                                worksheet.set_column('F:F', 40)  # Description
                                worksheet.set_column('G:G', 50)  # Recommendation
                                worksheet.set_column('H:H', 12)  # Impact
                                worksheet.set_column('I:I', 12)  # Effort
                                worksheet.set_column('J:J', 30)  # Expected Impact
                                worksheet.set_column('K:K', 20)  # Estimated Time
                                worksheet.set_column('L:L', 60)  # Action Steps
                                worksheet.set_column('M:M', 30)  # Tools Needed
                            elif sheet_name == 'Executive Summary':
                                worksheet.set_column('A:A', 20)  # Site
                                worksheet.set_column('B:B', 15)  # Overall Score
                                worksheet.set_column('C:H', 20)  # Other columns
                
                st.download_button(
                    label="📊 Download AI-Enhanced Excel Report",
                    data=output.getvalue(),
                    file_name=f"SEO_AI_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download comprehensive SEO analysis with AI recommendations in Excel format"
                )
            
            with col2:
                # Enhanced CSV export with AI data
                enhanced_export_data = []
                for data in comparison_data:
                    site_name = data['File Name'].replace('.csv', '').replace('.xlsx', '')
                    exec_summary = data['Executive Summary']
                    
                    # Get top 3 recommendations
                    top_recs = data['AI Recommendations'][:3] if data['AI Recommendations'] else []
                    top_rec_text = " | ".join([f"{rec['issue']}: {rec['recommendation']}" for rec in top_recs])
                    
                    enhanced_export_data.append({
                        'Site': site_name,
                        'Content SEO': data['Content SEO'],
                        'Technical SEO': data['Technical SEO'],
                        'User Experience': data['User Experience'],
                        'Overall Readiness': data['Overall Readiness'],
                        'Health Status': exec_summary['overall_health'],
                        'Critical Issues': exec_summary['critical_issues'],
                        'Quick Wins': exec_summary['quick_wins'],
                        'Potential Improvement': exec_summary['estimated_improvement'],
                        'Top 3 AI Recommendations': top_rec_text,
                        'Content Issues': data['Content Summary'],
                        'Technical Issues': data['Technical Summary'],
                        'UX Issues': data['UX Summary']
                    })
                
                enhanced_csv = pd.DataFrame(enhanced_export_data).to_csv(index=False)
                
                st.download_button(
                    label="📄 Download AI-Enhanced CSV Report",
                    data=enhanced_csv,
                    file_name=f"SEO_AI_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download AI-enhanced analysis results in CSV format"
                )
        
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

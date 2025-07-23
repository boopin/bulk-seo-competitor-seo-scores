import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        fig.add_trace(go.Scatterpolar(
            r=[row['Content SEO'], row['Technical SEO'], row['User Experience'], row['Overall Readiness']],
            theta=categories,
            fill='toself',
            name=row['File Name'].replace('.csv', '').replace('.xlsx', ''),
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
                # Prepare export data
                export_df = comparison_df.drop(['Content Details', 'Technical Details', 'UX Details'], axis=1)
                
                output = BytesIO()
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
            
            with col2:
                # CSV export
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV Report",
                    data=csv,
                    file_name=f"SEO_Comparison_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download analysis results in CSV format"
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

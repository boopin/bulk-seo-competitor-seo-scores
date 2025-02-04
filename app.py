import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

class SEOScorer:
    def __init__(self):
        self.weights = {
            'content_seo': 0.4,  # Adjusted weight after removing off-page SEO
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

def main():
    st.set_page_config(page_title="SEO Pulse", layout="wide")
    st.title("SEO Pulse")
    st.write("Transforming competitor SEO audits into actionable insights with precision and speed.")
    st.write("Upload Screaming Frog exports for your client and competitors to generate comparative scores and weaknesses.")

    uploaded_files = st.file_uploader("Upload Files", type=['csv', 'xlsx'], accept_multiple_files=True)

    if uploaded_files:
        comparison_data = []
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            scorer = SEOScorer()

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
                "UX Summary": scorer.summarize_category(ux_weaknesses)
            })

        comparison_df = pd.DataFrame(comparison_data)
        st.subheader("Comparison Table")
        st.dataframe(comparison_df)

        output = BytesIO()
        comparison_df.to_excel(output, index=False, engine='xlsxwriter')
        st.download_button(
            label="Download Comparison Report",
            data=output.getvalue(),
            file_name=f"SEO_Comparison_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()

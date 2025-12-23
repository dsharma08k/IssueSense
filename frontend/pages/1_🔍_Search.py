"""
Search Page - Clean Semantic Search Interface
"""

import streamlit as st
from api_client import api_client
from config import SESSION_TOKEN_KEY
import plotly.graph_objects as go

st.set_page_config(page_title="Search - IssueSense", page_icon="🔍", layout="wide")

# Clean minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { background: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: #e2e8f0 !important;
        color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    .page-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .page-subheader {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 24px;
    }
    
    /* Result Card */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.2s ease;
    }
    
    .result-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    /* Similarity Badge */
    .similarity-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .similarity-high {
        background: #dcfce7;
        color: #15803d;
    }
    
    .similarity-medium {
        background: #fef3c7;
        color: #b45309;
    }
    
    .similarity-low {
        background: #fee2e2;
        color: #b91c1c;
    }
    
    .result-title {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .result-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
    }
    
    .severity-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .severity-critical { background: #fee2e2; color: #b91c1c; }
    .severity-high { background: #fef3c7; color: #b45309; }
    .severity-medium { background: #fef9c3; color: #a16207; }
    .severity-low { background: #dcfce7; color: #15803d; }
    
    .stButton button {
        background: #3b82f6 !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stButton button:hover {
        background: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error("Please sign in first")
    st.stop()

# Header
st.markdown("""
    <div class="page-header">Search</div>
    <div class="page-subheader">Find similar issues with AI-powered semantic matching</div>
""", unsafe_allow_html=True)

# Search interface
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input(
        "Search query",
        placeholder="Describe the error (e.g., TypeError cannot read property undefined)",
        label_visibility="collapsed"
    )

with col2:
    threshold = st.slider("Match %", 0.1, 1.0, 0.3, 0.05, label_visibility="collapsed")

# Advanced filters
with st.expander("Advanced Filters", expanded=False):
    filter_cols = st.columns(4)
    
    with filter_cols[0]:
        filter_language = st.multiselect(
            "Language",
            ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Rust", "Ruby", "PHP"],
            default=[]
        )
    
    with filter_cols[1]:
        filter_severity = st.multiselect(
            "Severity",
            ["critical", "high", "medium", "low"],
            default=[]
        )
    
    with filter_cols[2]:
        filter_status = st.selectbox("Status", ["all", "open", "resolved"])
    
    with filter_cols[3]:
        filter_days = st.number_input("Last N days (0=all)", min_value=0, max_value=365, value=0)

if query:
    with st.spinner("🧠 Neural network analyzing..."):
        try:
            results = api_client.search_issues(query, threshold=threshold)
            
            # Apply filters
            if results:
                if filter_language:
                    results = [r for r in results if r['issue'].get('language') in filter_language]
                if filter_severity:
                    results = [r for r in results if r['issue'].get('severity') in filter_severity]
                if filter_status != "all":
                    results = [r for r in results if r['issue'].get('status') == filter_status]
            
            if results:
                st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <span style="font-family: 'Orbitron', sans-serif; color: #10b981; font-size: 1.2rem;">
                            ✓ {len(results)} MATCHES FOUND
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                for idx, item in enumerate(results):
                    issue = item['issue']
                    similarity = item['similarity']
                    sim_percent = int(similarity * 100)
                    
                    # Determine similarity class
                    if similarity >= 0.85:
                        sim_class = "similarity-high"
                        sim_label = "HIGH MATCH"
                    elif similarity >= 0.7:
                        sim_class = "similarity-medium"
                        sim_label = "GOOD MATCH"
                    else:
                        sim_class = "similarity-low"
                        sim_label = "PARTIAL"
                    
                    severity = issue.get('severity', 'medium')
                    
                    with st.container():
                        cols = st.columns([1, 6])
                        
                        with cols[0]:
                            st.markdown(f"""
                                <div class="similarity-ring {sim_class}" style="--percent: {sim_percent}%;">
                                    <div style="background: #0a0a0f; width: 60px; height: 60px; border-radius: 50%; 
                                         display: flex; align-items: center; justify-content: center; flex-direction: column;">
                                        <span style="font-size: 1rem;">{sim_percent}%</span>
                                        <span style="font-size: 0.5rem; opacity: 0.7;">{sim_label}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with cols[1]:
                            with st.expander(f"**{issue['error_type']}**: {issue['error_message'][:80]}...", expanded=(idx == 0)):
                                info_cols = st.columns([2, 1, 1, 1])
                                
                                with info_cols[0]:
                                    st.markdown(f"**Type:** `{issue['error_type']}`")
                                with info_cols[1]:
                                    st.markdown(f"**Lang:** {issue.get('language', 'N/A')}")
                                with info_cols[2]:
                                    st.markdown(f"""
                                        <span class="severity-badge severity-{severity}">{severity}</span>
                                    """, unsafe_allow_html=True)
                                with info_cols[3]:
                                    status_icon = "✅" if issue.get('status') == 'resolved' else "🔓"
                                    st.markdown(f"{status_icon} {issue.get('status', 'open').title()}")
                                
                                st.markdown(f"**Message:** {issue['error_message']}")
                                
                                if issue.get('stack_trace'):
                                    st.code(issue['stack_trace'][:500], language="python")
                                
                                if issue.get('tags'):
                                    tags_html = " ".join([f'<span style="background: rgba(6, 182, 212, 0.2); color: #06b6d4; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-right: 4px;">{tag}</span>' for tag in issue['tags']])
                                    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
                                
                                # Solutions
                                try:
                                    solutions = api_client.get_solutions(issue['id'])
                                    if solutions:
                                        st.markdown(f"**💡 {len(solutions)} Solution(s)**")
                                        for sol in solutions[:2]:
                                            st.markdown(f"→ {sol['title']} ({sol['effectiveness_score']:.0%})")
                                except:
                                    pass
                        
                        st.markdown("---")
            else:
                st.markdown("""
                    <div style="text-align: center; padding: 40px; color: #94a3b8;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">🔎</div>
                        <div style="font-family: 'JetBrains Mono', monospace;">No matches found. Try adjusting your search or threshold.</div>
                    </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")
else:
    # Empty state with example queries
    st.markdown("""
        <div style="text-align: center; padding: 40px; color: #94a3b8;">
            <div style="font-size: 4rem; margin-bottom: 15px;">🧠</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">
                Enter a search query to find similar errors using AI-powered semantic matching
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; font-family: 'Orbitron', sans-serif; color: #a855f7; margin-bottom: 20px;">
            ⚡ QUICK SEARCHES
        </div>
    """, unsafe_allow_html=True)
    
    examples = [
        "cannot read property undefined",
        "null pointer exception",
        "index out of bounds",
        "connection refused",
        "syntax error"
    ]
    
    cols = st.columns(len(examples))
    for idx, example in enumerate(examples):
        with cols[idx]:
            if st.button(f"'{example[:15]}...'", key=f"ex_{idx}", use_container_width=True):
                st.session_state['search_query'] = example
                st.rerun()

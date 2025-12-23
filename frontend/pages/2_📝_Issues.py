"""
Issues Page - Clean Error Management Interface
"""

import streamlit as st
from api_client import api_client
from datetime import datetime

st.set_page_config(page_title="Issues - IssueSense", page_icon="📝", layout="wide")

# Clean minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { background: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}
    
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
    
    /* Issue Card */
    .issue-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.2s ease;
    }
    
    .issue-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .issue-critical { border-left: 4px solid #ef4444; }
    .issue-high { border-left: 4px solid #f59e0b; }
    .issue-medium { border-left: 4px solid #eab308; }
    .issue-low { border-left: 4px solid #10b981; }
    
    .tag-chip {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-family: 'Inter', sans-serif;
        margin-right: 4px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-open { background: #fef3c7; color: #b45309; }
    .status-resolved { background: #dcfce7; color: #15803d; }
    .status-recurring { background: #fee2e2; color: #b91c1c; }
    
    .solution-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    
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
    <div class="page-header">Issues</div>
    <div class="page-subheader">Track and manage errors</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["All Issues", "Log New Issue"])

with tab1:
    # Filters
    filter_cols = st.columns([1, 1, 1, 2])
    
    with filter_cols[0]:
        status_filter = st.selectbox("Status", ["All", "open", "resolved", "recurring"])
    with filter_cols[1]:
        severity_filter = st.selectbox("Severity", ["All", "critical", "high", "medium", "low"])
    with filter_cols[2]:
        if st.button("🔄 REFRESH", use_container_width=True):
            st.rerun()
    with filter_cols[3]:
        if st.button("🔧 FIX SEARCH", use_container_width=True, help="Regenerate embeddings for old issues to enable search"):
            with st.spinner("Regenerating embeddings..."):
                try:
                    result = api_client.regenerate_embeddings()
                    st.success(f"✅ Fixed {result.get('updated', 0)} issues!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Fetch issues
    try:
        filters = {}
        if status_filter != "All":
            filters["status"] = status_filter
        if severity_filter != "All":
            filters["severity"] = severity_filter
        
        issues = api_client.list_issues(**filters)
        
        if issues:
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0; font-family: 'Orbitron', sans-serif; color: #10b981;">
                    ▸ {len(issues)} ERRORS TRACKED
                </div>
            """, unsafe_allow_html=True)
            
            for issue in issues:
                severity = issue.get('severity', 'medium')
                status = issue.get('status', 'open')
                
                severity_colors = {
                    'critical': '#ef4444',
                    'high': '#f59e0b',
                    'medium': '#eab308',
                    'low': '#10b981'
                }
                
                severity_icons = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }
                
                with st.expander(f"{severity_icons.get(severity, '⚪')} **{issue['error_type']}**: {issue['error_message'][:80]}...", expanded=False):
                    # Info row
                    info_cols = st.columns([2, 1, 1, 1])
                    
                    with info_cols[0]:
                        st.markdown(f"**Type:** `{issue['error_type']}`")
                    with info_cols[1]:
                        st.markdown(f"**Lang:** {issue.get('language', 'N/A')}")
                    with info_cols[2]:
                        st.markdown(f"""
                            <span class="status-badge status-{status}">{status}</span>
                        """, unsafe_allow_html=True)
                    with info_cols[3]:
                        st.markdown(f"**×{issue.get('occurrences', 1)}**")
                    
                    st.markdown(f"**Message:** {issue['error_message']}")
                    
                    # Stack trace
                    if issue.get('stack_trace'):
                        st.markdown("**Stack Trace:**")
                        st.code(issue['stack_trace'], language="python")
                    
                    # File info
                    if issue.get('file_path'):
                        st.markdown(f"**📁 File:** `{issue['file_path']}`" + 
                                   (f" **(Line {issue['line_number']})**" if issue.get('line_number') else ""))
                    
                    # Tags
                    if issue.get('tags'):
                        tags_html = " ".join([f'<span class="tag-chip">{tag}</span>' for tag in issue['tags']])
                        st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Solutions Section
                    st.markdown("### 💡 Solutions")
                    
                    try:
                        solutions = api_client.get_solutions(issue['id'])
                        
                        if solutions:
                            for idx, sol in enumerate(solutions, 1):
                                is_ai = sol.get('title', '').startswith('AI')
                                card_class = "solution-ai" if is_ai else "solution-card"
                                
                                st.markdown(f"""
                                    <div class="{card_class}">
                                        <strong>{'🤖 ' if is_ai else '💡 '}{sol['title']}</strong>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                if sol.get('description'):
                                    st.markdown(sol['description'])
                                
                                if sol.get('code_fix'):
                                    st.code(sol['code_fix'], language=issue.get('language', 'python').lower())
                                
                                # Effectiveness and voting
                                eff = sol.get('effectiveness_score', 0)
                                eff_color = '#10b981' if eff > 0.7 else '#f59e0b' if eff > 0.4 else '#ef4444'
                                
                                vote_cols = st.columns([3, 1, 1])
                                with vote_cols[0]:
                                    st.markdown(f"""
                                        <div style="font-size: 0.8rem; color: #94a3b8;">
                                            Effectiveness: <span style="color: {eff_color}; font-weight: bold;">{eff:.0%}</span>
                                        </div>
                                        <div class="effectiveness-meter">
                                            <div class="effectiveness-fill" style="width: {eff*100}%; background: {eff_color};"></div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                with vote_cols[1]:
                                    if st.button("👍", key=f"up_{sol['id']}"):
                                        try:
                                            api_client.add_feedback(sol['id'], was_helpful=True)
                                            st.rerun()
                                        except:
                                            pass
                                with vote_cols[2]:
                                    if st.button("👎", key=f"down_{sol['id']}"):
                                        try:
                                            api_client.add_feedback(sol['id'], was_helpful=False)
                                            st.rerun()
                                        except:
                                            pass
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                        else:
                            st.info("💭 No solutions yet")
                    except:
                        st.info("💭 No solutions yet")
                    
                    # AI Button
                    st.markdown("---")
                    ai_cols = st.columns([1, 3])
                    with ai_cols[0]:
                        if st.button("🤖 AI SOLVE", key=f"ai_{issue['id']}", use_container_width=True):
                            with st.spinner("🧠 AI analyzing..."):
                                try:
                                    result = api_client.suggest_and_save_solution(issue['id'])
                                    st.success("✅ AI solution generated!")
                                    st.rerun()
                                except Exception as e:
                                    error_msg = str(e)
                                    if "503" in error_msg or "unavailable" in error_msg:
                                        st.warning("⚠️ AI service unavailable - Add GROQ_API_KEY to backend .env")
                                    else:
                                        st.error(f"Error: {error_msg}")
                    with ai_cols[1]:
                        st.caption("Get instant AI-powered solution suggestion")
                    
                    # Add solution form
                    st.markdown("---")
                    with st.form(key=f"sol_form_{issue['id']}"):
                        st.markdown("**📝 Add Manual Solution**")
                        sol_title = st.text_input("Title*", key=f"sol_t_{issue['id']}")
                        sol_desc = st.text_area("Description", height=80, key=f"sol_d_{issue['id']}")
                        sol_code = st.text_area("Code Fix", height=80, key=f"sol_c_{issue['id']}")
                        
                        if st.form_submit_button("➕ ADD SOLUTION"):
                            if sol_title:
                                try:
                                    api_client.create_solution(issue['id'], {
                                        "title": sol_title,
                                        "description": sol_desc or None,
                                        "code_fix": sol_code or None
                                    })
                                    st.success("✅ Solution added!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.warning("Title required")
                    
                    # Actions
                    st.markdown("---")
                    action_cols = st.columns(3)
                    with action_cols[0]:
                        if issue['status'] != 'resolved':
                            if st.button("✅ RESOLVE", key=f"res_{issue['id']}"):
                                try:
                                    api_client.update_issue(issue['id'], {"status": "resolved"})
                                    st.rerun()
                                except:
                                    pass
                    with action_cols[1]:
                        if st.button("🗑️ DELETE", key=f"del_{issue['id']}"):
                            try:
                                api_client.delete_issue(issue['id'])
                                st.rerun()
                            except:
                                pass
                    
                    st.caption(f"Created: {issue['created_at'][:10]}")
        else:
            st.markdown("""
                <div style="text-align: center; padding: 60px; color: #94a3b8;">
                    <div style="font-size: 4rem; margin-bottom: 15px;">📭</div>
                    <div style="font-family: 'JetBrains Mono', monospace;">No errors logged. Use the LOG NEW ERROR tab to capture issues.</div>
                </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Failed to load issues: {str(e)}")

with tab2:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-family: 'Orbitron', sans-serif; color: #a855f7; font-size: 1.2rem;">
                ⚡ CAPTURE NEW ERROR
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("create_issue_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            error_type = st.text_input("Error Type*", placeholder="TypeError, ValueError, etc.")
            language = st.selectbox("Language", [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#",
                "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Other"
            ])
            severity = st.selectbox("Severity*", ["medium", "low", "high", "critical"])
        
        with col2:
            framework = st.text_input("Framework", placeholder="React, Django, etc.")
            environment = st.text_input("Environment", placeholder="development, production")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="backend, api")
        
        error_message = st.text_area("Error Message*", placeholder="Describe the error...", height=100)
        stack_trace = st.text_area("Stack Trace", placeholder="Paste the full stack trace...", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            file_path = st.text_input("File Path", placeholder="/path/to/file.py")
        with col2:
            line_number = st.number_input("Line Number", min_value=0, value=0)
        
        code_snippet = st.text_area("Code Snippet", placeholder="Relevant code...", height=100)
        
        submitted = st.form_submit_button("🚀 LOG ERROR", use_container_width=True)
        
        if submitted:
            if not error_type or not error_message:
                st.error("❌ Error Type and Message are required")
            else:
                try:
                    issue_data = {
                        "error_type": error_type,
                        "error_message": error_message,
                        "stack_trace": stack_trace or None,
                        "language": language if language != "Other" else None,
                        "framework": framework or None,
                        "environment": environment or None,
                        "file_path": file_path or None,
                        "line_number": line_number if line_number > 0 else None,
                        "code_snippet": code_snippet or None,
                        "tags": [t.strip() for t in tags_input.split(",")] if tags_input else [],
                        "severity": severity
                    }
                    
                    result = api_client.create_issue(issue_data)
                    
                    if result.get('is_duplicate'):
                        st.warning(f"🔄 Duplicate detected! Updated occurrence count to **{result['issue']['occurrences']}**")
                    else:
                        st.success("✅ Error logged successfully!")
                        if result.get('similar_issues'):
                            st.info(f"💡 Found {len(result['similar_issues'])} similar issues")
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)}")

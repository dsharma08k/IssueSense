"""
Analytics Page - Clean Data Visualizations
"""

import streamlit as st
from api_client import api_client
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Analytics - IssueSense", page_icon="📊", layout="wide")

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
    
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .stat-card h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .stat-card p {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    .stat-card.blue { border-left: 4px solid #3b82f6; }
    .stat-card.green { border-left: 4px solid #10b981; }
    .stat-card.yellow { border-left: 4px solid #f59e0b; }
    .stat-card.red { border-left: 4px solid #ef4444; }
    
    .chart-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 15px;
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
    
    .stat-orb {
        background: #ffffff;
        border: 2px solid rgba(168, 85, 247, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .stat-orb h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .stat-orb p {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error("Please sign in first")
    st.stop()

# Header
st.markdown("""
    <div class="page-header">Analytics</div>
    <div class="page-subheader">Insights and trends from your error data</div>
""", unsafe_allow_html=True)

try:
    # Fetch data
    stats = api_client.get_dashboard_stats()
    trends = api_client.get_trends(days=7)
    languages = api_client.get_language_distribution()
    
    # Stat Orbs Row
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown(f"""
            <div class="stat-orb">
                <h1>{stats['total_issues']}</h1>
                <p>Total Errors</p>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
            <div class="stat-orb" style="border-color: rgba(16, 185, 129, 0.4);">
                <h1 style="color: #10b981;">
                    {stats['resolved_issues']}
                </h1>
                <p>Resolved</p>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
            <div class="stat-orb" style="border-color: rgba(245, 158, 11, 0.4);">
                <h1 style="color: #f59e0b;">
                    {stats['open_issues']}
                </h1>
                <p>Open</p>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        rate = int(stats['resolution_rate'] * 100)
        rate_color = "#10b981" if rate >= 70 else "#f59e0b" if rate >= 40 else "#ef4444"
        st.markdown(f"""
            <div class="stat-orb" style="border-color: rgba(6, 182, 212, 0.4);">
                <h1 style="color: {rate_color};">
                    {rate}%
                </h1>
                <p>Resolution Rate</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-title">📈 ERROR TREND (7 DAYS)</div>', unsafe_allow_html=True)
        
        if trends:
            dates = [t['date'] for t in trends]
            totals = [t['total'] for t in trends]
            resolved = [t['resolved'] for t in trends]
            
            fig = go.Figure()
            
            # Total line with glow effect
            fig.add_trace(go.Scatter(
                x=dates, y=totals, mode='lines+markers',
                name='Total', 
                line=dict(color='#a855f7', width=3, shape='spline'),
                marker=dict(size=10, color='#a855f7', line=dict(width=2, color='#ffffff')),
                fill='tozeroy',
                fillcolor='rgba(168, 85, 247, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=resolved, mode='lines+markers',
                name='Resolved', 
                line=dict(color='#10b981', width=2, shape='spline'),
                marker=dict(size=8, color='#10b981')
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, color='#64748b'),
                yaxis=dict(showgrid=True, gridcolor='rgba(168, 85, 247, 0.1)', color='#64748b'),
                hovermode='x unified',
                font=dict(family='JetBrains Mono, monospace')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available")
    
    with col2:
        st.markdown('<div class="chart-title">🎯 SEVERITY DISTRIBUTION</div>', unsafe_allow_html=True)
        
        severity_data = stats['issues_by_severity']
        
        if sum(severity_data.values()) > 0:
            # Create gauge-like donut chart
            fig = go.Figure(data=[go.Pie(
                labels=['Critical', 'High', 'Medium', 'Low'],
                values=[
                    severity_data.get('critical', 0),
                    severity_data.get('high', 0),
                    severity_data.get('medium', 0),
                    severity_data.get('low', 0)
                ],
                hole=0.6,
                marker=dict(
                    colors=['#ef4444', '#f59e0b', '#eab308', '#10b981'],
                    line=dict(color='#0a0a0f', width=2)
                ),
                textinfo='label+value',
                textposition='outside',
                textfont=dict(family='JetBrains Mono', size=11),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
            )])
            
            # Add center text
            fig.add_annotation(
                text=f"<b>{stats['total_issues']}</b><br>Total",
                x=0.5, y=0.5,
                font=dict(family='Orbitron', size=24, color='#a855f7'),
                showarrow=False
            )
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                font=dict(family='JetBrains Mono, monospace')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No severity data")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-title">💻 LANGUAGE DISTRIBUTION</div>', unsafe_allow_html=True)
        
        if languages:
            lang_names = [l['language'] or 'Unknown' for l in languages[:8]]
            lang_counts = [l['count'] for l in languages[:8]]
            
            # Horizontal bar with gradient
            fig = go.Figure(data=[go.Bar(
                x=lang_counts,
                y=lang_names,
                orientation='h',
                marker=dict(
                    color=lang_counts,
                    colorscale=[[0, '#06b6d4'], [0.5, '#a855f7'], [1, '#ec4899']],
                    line=dict(width=0)
                ),
                text=lang_counts,
                textposition='outside',
                textfont=dict(family='Orbitron', color='#e2e8f0')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=0, r=40, t=10, b=0),
                xaxis=dict(showgrid=True, gridcolor='rgba(168, 85, 247, 0.1)', color='#64748b'),
                yaxis=dict(showgrid=False, color='#e2e8f0'),
                font=dict(family='JetBrains Mono, monospace'),
                bargap=0.3
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No language data")
    
    with col2:
        st.markdown('<div class="chart-title">🔥 TOP ERROR TYPES</div>', unsafe_allow_html=True)
        
        top_errors = stats['top_error_types'][:8]
        
        if top_errors:
            error_types = [e['type'] for e in top_errors]
            error_counts = [e['count'] for e in top_errors]
            
            fig = go.Figure(data=[go.Bar(
                x=error_counts,
                y=error_types,
                orientation='h',
                marker=dict(
                    color=error_counts,
                    colorscale=[[0, '#f59e0b'], [0.5, '#ef4444'], [1, '#dc2626']],
                    line=dict(width=0)
                ),
                text=error_counts,
                textposition='outside',
                textfont=dict(family='Orbitron', color='#e2e8f0')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=0, r=40, t=10, b=0),
                xaxis=dict(showgrid=True, gridcolor='rgba(239, 68, 68, 0.1)', color='#64748b'),
                yaxis=dict(showgrid=False, color='#e2e8f0'),
                font=dict(family='JetBrains Mono, monospace'),
                bargap=0.3
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No error type data")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Resolution Rate Gauge
    st.markdown('<div class="chart-title">⚡ RESOLUTION PERFORMANCE</div>', unsafe_allow_html=True)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=stats['resolution_rate'] * 100,
        number=dict(suffix="%", font=dict(family='Orbitron', size=48, color='#a855f7')),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor='#64748b', tickfont=dict(color='#64748b')),
            bar=dict(color='#a855f7'),
            bgcolor='rgba(168, 85, 247, 0.1)',
            borderwidth=2,
            bordercolor='rgba(168, 85, 247, 0.3)',
            steps=[
                dict(range=[0, 40], color='rgba(239, 68, 68, 0.2)'),
                dict(range=[40, 70], color='rgba(245, 158, 11, 0.2)'),
                dict(range=[70, 100], color='rgba(16, 185, 129, 0.2)')
            ],
            threshold=dict(
                line=dict(color='#06b6d4', width=4),
                thickness=0.75,
                value=stats['resolution_rate'] * 100
            )
        )
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=30, r=30, t=30, b=0),
        font=dict(family='JetBrains Mono, monospace')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights Row
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-title">💡 KEY INSIGHTS</div>', unsafe_allow_html=True)
    
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        if stats['resolution_rate'] >= 0.7:
            st.markdown("""
                <div class="insight-card">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">🎉</div>
                    <div style="font-family: 'JetBrains Mono', monospace; color: #10b981; font-size: 0.85rem;">
                        Excellent resolution rate!
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="insight-card insight-warning">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">⚠️</div>
                    <div style="font-family: 'JetBrains Mono', monospace; color: #f59e0b; font-size: 0.85rem;">
                        Resolution rate needs improvement
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with insight_cols[1]:
        critical_count = severity_data.get('critical', 0)
        if critical_count > 0:
            st.markdown(f"""
                <div class="insight-card insight-warning">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">🔴</div>
                    <div style="font-family: 'JetBrains Mono', monospace; color: #ef4444; font-size: 0.85rem;">
                        {critical_count} critical issue(s) need attention!
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="insight-card">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">✅</div>
                    <div style="font-family: 'JetBrains Mono', monospace; color: #10b981; font-size: 0.85rem;">
                        No critical issues!
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with insight_cols[2]:
        if top_errors:
            most_common = top_errors[0]
            st.markdown(f"""
                <div class="insight-card">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">📌</div>
                    <div style="font-family: 'JetBrains Mono', monospace; color: #06b6d4; font-size: 0.85rem;">
                        Most common: {most_common['type'][:20]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Failed to load analytics: {str(e)}")
    st.markdown("""
        <div style="text-align: center; padding: 40px; color: #94a3b8;">
            <div style="font-size: 3rem; margin-bottom: 15px;">📊</div>
            <div style="font-family: 'JetBrains Mono', monospace;">
                Make sure the backend API is running and you have created some issues.
            </div>
        </div>
    """, unsafe_allow_html=True)

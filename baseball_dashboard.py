import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import numpy as np

class BaseballDashboard:
    def __init__(self, csv_file_path):
        self.df = pd.read_csv(csv_file_path)
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def get_modern_theme(self):
        """Define modern color theme and styling"""
        return {
            'primary': '#1f2937',      # Dark blue-gray
            'secondary': '#3b82f6',    # Blue
            'accent': '#10b981',       # Green
            'background': '#f8fafc',   # Light gray
            'surface': '#ffffff',      # White
            'text_primary': '#1f2937', # Dark gray
            'text_secondary': '#6b7280', # Medium gray
            'border': '#e5e7eb',       # Light border
            'shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
        }
    
    def setup_layout(self):
        theme = self.get_modern_theme()
        players = sorted(self.df['Player'].unique()) if 'Player' in self.df.columns else sorted(self.df.index)
        
        self.app.layout = html.Div([
            # Custom CSS
            html.Div([
                html.Style("""
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                    
                    * {
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    }
                    
                    body {
                        margin: 0;
                        padding: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }
                    
                    .main-container {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }
                    
                    .content-wrapper {
                        max-width: 1400px;
                        margin: 0 auto;
                        background: rgba(255, 255, 255, 0.95);
                        border-radius: 20px;
                        padding: 30px;
                        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                        backdrop-filter: blur(10px);
                    }
                    
                    .control-card {
                        background: linear-gradient(145deg, #ffffff, #f1f5f9);
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        transition: all 0.3s ease;
                    }
                    
                    .control-card:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                    }
                    
                    .stat-card {
                        background: linear-gradient(145deg, #ffffff, #f8fafc);
                        border-radius: 15px;
                        padding: 25px;
                        margin: 8px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.5);
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .stat-card::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 4px;
                        background: linear-gradient(90deg, #3b82f6, #10b981);
                    }
                    
                    .stat-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
                    }
                    
                    .chart-container {
                        background: linear-gradient(145deg, #ffffff, #f8fafc);
                        border-radius: 15px;
                        padding: 20px;
                        margin: 10px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.5);
                        transition: all 0.3s ease;
                    }
                    
                    .chart-container:hover {
                        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
                    }
                    
                    .Select-control {
                        border-radius: 10px !important;
                        border: 2px solid #e5e7eb !important;
                        transition: all 0.3s ease !important;
                    }
                    
                    .Select-control:hover {
                        border-color: #3b82f6 !important;
                    }
                """)
            ]),
            
            # Main container
            html.Div([
                # Header
                html.Div([
                    html.H1("⚾ Baseball Analytics Dashboard", 
                           style={
                               'textAlign': 'center',
                               'marginBottom': '10px',
                               'fontSize': '3rem',
                               'fontWeight': '700',
                               'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                               'backgroundClip': 'text',
                               'WebkitBackgroundClip': 'text',
                               'WebkitTextFillColor': 'transparent',
                               'textShadow': '0 4px 8px rgba(0,0,0,0.1)'
                           }),
                    html.P("Advanced Player Performance Analytics", 
                          style={
                              'textAlign': 'center',
                              'color': theme['text_secondary'],
                              'fontSize': '1.2rem',
                              'marginBottom': '40px',
                              'fontWeight': '400'
                          })
                ]),
                
                # Controls Section
                html.Div([
                    html.Div([
                        html.Div([
                            html.Label("🏃‍♂️ Select Player", 
                                     style={'fontSize': '1.1rem', 'fontWeight': '600', 'color': theme['text_primary'], 'marginBottom': '10px', 'display': 'block'}),
                            dcc.Dropdown(
                                id='player-dropdown',
                                options=[{'label': f"⭐ {player}", 'value': player} for player in players],
                                value=players[0] if players else None,
                                style={'borderRadius': '10px'},
                                className='modern-dropdown'
                            )
                        ], className='control-card', style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.Label("📊 Statistics to Compare", 
                                     style={'fontSize': '1.1rem', 'fontWeight': '600', 'color': theme['text_primary'], 'marginBottom': '10px', 'display': 'block'}),
                            dcc.Dropdown(
                                id='stats-dropdown',
                                options=[
                                    {'label': '🎯 On Base Percentage (OBP)', 'value': 'OBP'},
                                    {'label': '⚾ Batting Average (AVG)', 'value': 'AVG'},
                                    {'label': '🍀 BABIP', 'value': 'BABIP'},
                                    {'label': '💪 Slugging (SLUG)', 'value': 'SLUG'},
                                    {'label': '🔥 OPS', 'value': 'OPS'},
                                    {'label': '⚡ Doubles (2B)', 'value': '2B'},
                                    {'label': '🚀 Home Runs (HR)', 'value': 'HR'},
                                    {'label': '🏃 RBI', 'value': 'RBI'},
                                    {'label': '💨 Stolen Bases (SB)', 'value': 'SB'}
                                ],
                                value=['OBP', 'AVG', 'SLUG'],
                                multi=True,
                                style={'borderRadius': '10px'}
                            )
                        ], className='control-card', style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.Label("📅 Season Range", 
                                     style={'fontSize': '1.1rem', 'fontWeight': '600', 'color': theme['text_primary'], 'marginBottom': '15px', 'display': 'block'}),
                            dcc.RangeSlider(
                                id='season-slider',
                                min=self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                                max=self.df['Season'].max() if 'Season' in self.df.columns else 2023,
                                value=[self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                                       self.df['Season'].max() if 'Season' in self.df.columns else 2023],
                                marks={i: {'label': str(i), 'style': {'color': theme['text_primary'], 'fontWeight': '500'}} 
                                       for i in range(
                                           self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                                           self.df['Season'].max() + 1 if 'Season' in self.df.columns else 2024
                                       )},
                                step=1,
                                tooltip={'placement': 'bottom'},
                                className='modern-slider'
                            )
                        ], className='control-card', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ], style={'marginBottom': '40px'}),
                    
                    # Player stats overview
                    html.Div(id='player-stats-overview', style={'marginBottom': '30px'}),
                    
                    # Charts Section
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Graph(id='batting-average-trend', config={'displayModeBar': False})
                            ], className='chart-container')
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='power-stats-chart', config={'displayModeBar': False})
                            ], className='chart-container')
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ]),
                    
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Graph(id='radar-chart', config={'displayModeBar': False})
                            ], className='chart-container')
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='comparison-chart', config={'displayModeBar': False})
                            ], className='chart-container')
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ]),
                    
                    html.Div([
                        html.Div([
                            dcc.Graph(id='correlation-heatmap', config={'displayModeBar': False})
                        ], className='chart-container')
                    ], style={'width': '100%'})
                ])
            ], className='content-wrapper')
        ], className='main-container')
    
    def get_modern_chart_layout(self, title):
        """Get modern chart layout template"""
        return {
            'title': {
                'text': title,
                'font': {'size': 18, 'family': 'Inter, sans-serif', 'color': '#1f2937'},
                'x': 0.5,
                'xanchor': 'center'
            },
            'font': {'family': 'Inter, sans-serif', 'color': '#374151'},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60},
            'xaxis': {
                'gridcolor': '#f3f4f6',
                'linecolor': '#e5e7eb',
                'tickfont': {'color': '#6b7280'}
            },
            'yaxis': {
                'gridcolor': '#f3f4f6',
                'linecolor': '#e5e7eb',
                'tickfont': {'color': '#6b7280'}
            }
        }
    
    def setup_callbacks(self):
        @self.app.callback(
            [Output('player-stats-overview', 'children'),
             Output('batting-average-trend', 'figure'),
             Output('power-stats-chart', 'figure'),
             Output('radar-chart', 'figure'),
             Output('comparison-chart', 'figure'),
             Output('correlation-heatmap', 'figure')],
            [Input('player-dropdown', 'value'),
             Input('stats-dropdown', 'value'),
             Input('season-slider', 'value')]
        )
        def update_dashboard(selected_player, selected_stats, season_range):
            filtered_df = self.df.copy()
            if 'Season' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['Season'] >= season_range[0]) & 
                    (filtered_df['Season'] <= season_range[1])
                ]
            
            player_data = filtered_df[filtered_df['Player'] == selected_player] if 'Player' in filtered_df.columns else filtered_df
            
            overview = self.create_stats_overview(player_data, selected_player)
            trend_fig = self.create_batting_trend(player_data)
            power_fig = self.create_power_stats(player_data)
            radar_fig = self.create_radar_chart(player_data, selected_stats)
            comparison_fig = self.create_comparison_chart(filtered_df, selected_player, selected_stats)
            heatmap_fig = self.create_correlation_heatmap(player_data)
            
            return overview, trend_fig, power_fig, radar_fig, comparison_fig, heatmap_fig
    
    def create_stats_overview(self, player_data, player_name):
        if player_data.empty:
            return html.Div("No data available for selected filters")
        
        latest_stats = player_data.iloc[-1] if len(player_data) > 0 else player_data.iloc[0]
        
        stats_info = [
            {'stat': 'AVG', 'emoji': '⚾', 'color': '#3b82f6'},
            {'stat': 'OBP', 'emoji': '🎯', 'color': '#10b981'},
            {'stat': 'SLUG', 'emoji': '💪', 'color': '#f59e0b'},
            {'stat': 'OPS', 'emoji': '🔥', 'color': '#ef4444'},
            {'stat': 'HR', 'emoji': '🚀', 'color': '#8b5cf6'},
            {'stat': 'RBI', 'emoji': '🏃', 'color': '#06b6d4'}
        ]
        
        stats_cards = []
        for info in stats_info:
            if info['stat'] in latest_stats:
                value = latest_stats[info['stat']]
                formatted_value = f"{value:.3f}" if isinstance(value, float) and value < 10 else str(int(value))
                
                stats_cards.append(
                    html.Div([
                        html.Div([
                            html.Span(info['emoji'], style={'fontSize': '2rem', 'marginBottom': '10px', 'display': 'block'}),
                            html.H3(formatted_value, style={
                                'fontSize': '2rem',
                                'fontWeight': '700',
                                'margin': '0',
                                'color': info['color']
                            }),
                            html.P(info['stat'], style={
                                'fontSize': '0.9rem',
                                'fontWeight': '600',
                                'margin': '8px 0 0 0',
                                'color': '#6b7280',
                                'textTransform': 'uppercase',
                                'letterSpacing': '1px'
                            })
                        ])
                    ], className='stat-card', style={
                        'width': '15%',
                        'display': 'inline-block',
                        'textAlign': 'center',
                        'verticalAlign': 'top'
                    })
                )
        
        return html.Div([
            html.Div([
                html.H2([
                    html.Span("🌟 ", style={'marginRight': '10px'}),
                    f"{player_name}",
                    html.Span(" - Performance Overview", style={'color': '#6b7280', 'fontWeight': '400'})
                ], style={
                    'textAlign': 'center',
                    'fontSize': '2.2rem',
                    'fontWeight': '700',
                    'marginBottom': '30px',
                    'color': '#1f2937'
                }),
                html.Div(stats_cards, style={'textAlign': 'center', 'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
            ])
        ])
    
    def create_batting_trend(self, player_data):
        fig = go.Figure()
        colors = ['#3b82f6', '#10b981', '#f59e0b']
        
        if 'Season' in player_data.columns and len(player_data) > 1:
            for i, stat in enumerate(['AVG', 'OBP', 'SLUG']):
                if stat in player_data.columns:
                    fig.add_trace(go.Scatter(
                        x=player_data['Season'],
                        y=player_data[stat],
                        mode='lines+markers',
                        name=stat,
                        line=dict(width=4, color=colors[i]),
                        marker=dict(size=8, color=colors[i], line=dict(width=2, color='white')),
                        hovertemplate=f'<b>{stat}</b><br>Season: %{{x}}<br>Value: %{{y:.3f}}<extra></extra>'
                    ))
        else:
            stats = ['AVG', 'OBP', 'SLUG']
            values = [player_data[stat].iloc[0] if stat in player_data.columns else 0 for stat in stats]
            fig.add_trace(go.Bar(
                x=stats, 
                y=values, 
                name='Current Stats',
                marker=dict(color=colors, opacity=0.8, line=dict(width=2, color='white'))
            ))
        
        layout = self.get_modern_chart_layout('📈 Batting Statistics Trend')
        fig.update_layout(**layout)
        
        return fig
    
    def create_power_stats(self, player_data):
        fig = make_subplots(rows=1, cols=2, subplot_titles=('🚀 Home Runs', '⚡ Extra Base Hits'))
        
        if 'Season' in player_data.columns and len(player_data) > 1:
            if 'HR' in player_data.columns:
                fig.add_trace(go.Bar(
                    x=player_data['Season'],
                    y=player_data['HR'],
                    name='HR',
                    marker=dict(color='#ef4444', opacity=0.8, line=dict(width=2, color='white'))
                ), row=1, col=1)
            
            extra_base = []
            for _, row in player_data.iterrows():
                xbh = 0
                if '2B' in row: xbh += row['2B'] if pd.notna(row['2B']) else 0
                if '3B' in row: xbh += row['3B'] if pd.notna(row['3B']) else 0
                if 'HR' in row: xbh += row['HR'] if pd.notna(row['HR']) else 0
                extra_base.append(xbh)
            
            fig.add_trace(go.Bar(
                x=player_data['Season'],
                y=extra_base,
                name='XBH',
                marker=dict(color='#3b82f6', opacity=0.8, line=dict(width=2, color='white'))
            ), row=1, col=2)
        else:
            hr_val = player_data['HR'].iloc[0] if 'HR' in player_data.columns else 0
            fig.add_trace(go.Bar(
                x=['HR'], 
                y=[hr_val], 
                marker=dict(color='#ef4444', opacity=0.8, line=dict(width=2, color='white'))
            ), row=1, col=1)
            
            xbh_val = 0
            if '2B' in player_data.columns: xbh_val += player_data['2B'].iloc[0] or 0
            if '3B' in player_data.columns: xbh_val += player_data['3B'].iloc[0] or 0
            if 'HR' in player_data.columns: xbh_val += player_data['HR'].iloc[0] or 0
            fig.add_trace(go.Bar(
                x=['XBH'], 
                y=[xbh_val], 
                marker=dict(color='#3b82f6', opacity=0.8, line=dict(width=2, color='white'))
            ), row=1, col=2)
        
        layout = self.get_modern_chart_layout('💪 Power Statistics')
        layout['showlegend'] = False
        fig.update_layout(**layout)
        
        return fig
    
    def create_radar_chart(self, player_data, selected_stats):
        if player_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False, font={'size': 16, 'color': '#6b7280'})
            return fig
        
        latest_data = player_data.iloc[-1]
        radar_stats = selected_stats if selected_stats else ['AVG', 'OBP', 'SLUG', 'OPS']
        
        values = []
        categories = []
        
        for stat in radar_stats:
            if stat in latest_data and pd.notna(latest_data[stat]):
                if stat in ['AVG', 'OBP', 'SLUG', 'BABIP']:
                    normalized_val = min(latest_data[stat] / 0.400, 1.0)
                elif stat == 'OPS':
                    normalized_val = min(latest_data[stat] / 1.000, 1.0)
                else:
                    normalized_val = min(latest_data[stat] / 50, 1.0)
                
                values.append(normalized_val)
                categories.append(stat)
        
        if values:
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Player Stats',
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=3),
                marker=dict(color='#3b82f6', size=8, line=dict(width=2, color='white'))
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        gridcolor='#f3f4f6',
                        linecolor='#e5e7eb'
                    ),
                    angularaxis=dict(
                        gridcolor='#f3f4f6',
                        linecolor='#e5e7eb'
                    )
                ),
                title={
                    'text': '🎯 Player Performance Radar',
                    'font': {'size': 18, 'family': 'Inter, sans-serif', 'color': '#1f2937'},
                    'x': 0.5
                },
                font={'family': 'Inter, sans-serif'},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
        else:
            fig = go.Figure()
            fig.add_annotation(text="No valid stats for radar chart", showarrow=False)
        
        return fig
    
    def create_comparison_chart(self, full_df, selected_player, selected_stats):
        if not selected_stats:
            fig = go.Figure()
            fig.add_annotation(text="Select stats to compare", showarrow=False, font={'size': 16, 'color': '#6b7280'})
            return fig
        
        league_avg = full_df[selected_stats].mean()
        player_data = full_df[full_df['Player'] == selected_player] if 'Player' in full_df.columns else full_df
        player_avg = player_data[selected_stats].mean()
        
        fig = go.Figure(data=[
            go.Bar(
                name='League Average', 
                x=selected_stats, 
                y=league_avg,
                marker=dict(color='#94a3b8', opacity=0.7, line=dict(width=2, color='white')),
                text=[f'{val:.3f}' if val < 10 else f'{val:.0f}' for val in league_avg],
                textposition='auto'
            ),
            go.Bar(
                name='Player Average', 
                x=selected_stats, 
                y=player_avg,
                marker=dict(color='#3b82f6', opacity=0.8, line=dict(width=2, color='white')),
                text=[f'{val:.3f}' if val < 10 else f'{val:.0f}' for val in player_avg],
                textposition='auto'
            )
        ])
        
        layout = self.get_modern_chart_layout('📊 Player vs League Comparison')
        layout['barmode'] = 'group'
        layout['legend'] = {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        }
        fig.update_layout(**layout)
        
        return fig
    
    def create_correlation_heatmap(self, player_data):
        numeric_columns = player_data.select_dtypes(include=[np.number]).columns
        correlation_data = player_data[numeric_columns].corr()
        
        fig = px.imshow(
            correlation_data,
            title="🔥 Statistics Correlation Heatmap",
            color_continuous_scale='RdBu',
            aspect='auto',
            text_auto='.2f'
        )
        
        fig.update_layout(
            title={
                'text': '🔥 Statistics Correlation Heatmap',
                'font': {'size': 18, 'family': 'Inter, sans-serif', 'color': '#1f2937'},
                'x': 0.5
            },
            font={'family': 'Inter, sans-serif'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin={'l': 80, 'r': 80, 't': 80, 'b': 80}
        )
        
        return fig
    
    def run(self, debug=False, port=8050):
        self.app.run(debug=debug, port=port)

# Sample data generator for testing
def generate_sample_data():
    """Generate sample baseball data for testing"""
    import random
    
    players = ['Mike Trout', 'Mookie Betts', 'Juan Soto', 'Aaron Judge', 'Vladimir Guerrero Jr.']
    seasons = [2021, 2022, 2023]
    
    data = []
    for player in players:
        for season in seasons:
            data.append({
                'Player': player,
                'Season': season,
                'AVG': round(random.uniform(0.250, 0.350), 3),
                'OBP': round(random.uniform(0.300, 0.450), 3),
                'SLUG': round(random.uniform(0.400, 0.650), 3),
                'OPS': round(random.uniform(0.700, 1.100), 3),
                'BABIP': round(random.uniform(0.250, 0.400), 3),
                'HR': random.randint(15, 50),
                '2B': random.randint(20, 45),
                '3B': random.randint(0, 8),
                'RBI': random.randint(60, 130),
                'SB': random.randint(0, 25),
                'BB': random.randint(40, 120),
                'SO': random.randint(80, 200)
            })
    
    df = pd.DataFrame(data)
    df['OPS'] = df['OBP'] + df['SLUG']  # Recalculate OPS to be accurate
    return df

# Usage example
if __name__ == "__main__":
    # Option 1: Use your own CSV file
    # dashboard = BaseballDashboard('your_baseball_data.csv')
    
    # Option 2: Generate sample data for testing
    sample_data = generate_sample_data()
    sample_data.to_csv('sample_baseball_data.csv', index=False)
    
    dashboard = BaseballDashboard('sample_baseball_data.csv')
    
    print("🚀 Starting Baseball Analytics Dashboard...")
    print("✨ Dashboard Features:")
    print("   📊 Interactive player statistics")
    print("   📈 Performance trends over time")
    print("   🎯 Player vs league comparisons")
    print("   🔥 Advanced correlation analysis")
    print("")
    print("🌐 Open your browser and navigate to: http://127.0.0.1:8050")
    print("⚾ Enjoy exploring your baseball data!")
    print("")
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using Baseball Analytics!")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("💡 Try updating your packages: pip install --upgrade dash plotly pandas")
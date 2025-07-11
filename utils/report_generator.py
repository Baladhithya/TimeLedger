import json
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

class ReportGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def generate_daily_report(self, target_date=None):
        """Generate comprehensive daily report"""
        if target_date is None:
            target_date = datetime.now().date()
        
        # Load data for the target date
        self.data_manager.load_daily_data(target_date)
        
        report_data = {
            "date": target_date.isoformat(),
            "summary": self._generate_daily_summary(),
            "app_usage": self._generate_app_usage_analysis(),
            "productivity": self._generate_productivity_analysis(),
            "resource_usage": self._generate_resource_analysis(),
            "timeline": self._generate_timeline_data()
        }
        
        # Generate HTML report
        html_content = self._generate_html_report(report_data)
        
        # Save report
        report_filename = f"daily_report_{target_date.isoformat()}.html"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_daily_summary(self):
        """Generate daily summary statistics"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return {
                "total_time": 0,
                "active_time": 0,
                "apps_used": 0,
                "most_used_app": "None"
            }
        
        total_time = sum(s['duration_seconds'] for s in sessions)
        active_time = sum(s['duration_seconds'] for s in sessions if s['was_active'])
        
        # Count app usage
        app_times = defaultdict(int)
        for session in sessions:
            app_times[session['app_name']] += session['duration_seconds']
        
        most_used_app = max(app_times.items(), key=lambda x: x[1])[0] if app_times else "None"
        
        return {
            "total_time": total_time,
            "active_time": active_time,
            "apps_used": len(app_times),
            "most_used_app": most_used_app,
            "productivity_ratio": (active_time / total_time * 100) if total_time > 0 else 0
        }
    
    def _generate_app_usage_analysis(self):
        """Generate detailed app usage analysis"""
        sessions = self.data_manager.app_sessions
        app_data = defaultdict(lambda: {
            "total_time": 0,
            "active_time": 0,
            "sessions": 0,
            "category": "Other"
        })
        
        # Categorize apps
        categories = {
            "Productivity": ["notepad", "word", "excel", "powerpoint", "code", "sublime", "atom", "vscode"],
            "Web Browsing": ["chrome", "firefox", "edge", "safari", "opera"],
            "Communication": ["slack", "teams", "discord", "skype", "zoom"],
            "Entertainment": ["spotify", "vlc", "netflix", "youtube", "steam"],
            "Development": ["python", "java", "git", "docker", "terminal", "cmd"]
        }
        
        for session in sessions:
            app_name = session['app_name']
            duration = session['duration_seconds']
            
            app_data[app_name]["total_time"] += duration
            app_data[app_name]["sessions"] += 1
            
            if session['was_active']:
                app_data[app_name]["active_time"] += duration
            
            # Categorize app
            for category, keywords in categories.items():
                if any(keyword in app_name.lower() for keyword in keywords):
                    app_data[app_name]["category"] = category
                    break
        
        # Convert to sorted list
        sorted_apps = sorted(app_data.items(), key=lambda x: x[1]["total_time"], reverse=True)
        
        return {app: data for app, data in sorted_apps[:20]}  # Top 20 apps
    
    def _generate_productivity_analysis(self):
        """Analyze productivity patterns"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return {"score": 0, "insights": []}
        
        # Calculate hourly productivity
        hourly_data = defaultdict(lambda: {"productive": 0, "total": 0})
        
        productive_apps = ["notepad", "word", "excel", "code", "sublime", "atom", "vscode"]
        
        for session in sessions:
            start_time = datetime.fromisoformat(session['start_time'])
            hour = start_time.hour
            duration = session['duration_seconds']
            
            hourly_data[hour]["total"] += duration
            
            if any(app in session['app_name'].lower() for app in productive_apps):
                hourly_data[hour]["productive"] += duration
        
        # Calculate overall productivity score
        total_time = sum(data["total"] for data in hourly_data.values())
        productive_time = sum(data["productive"] for data in hourly_data.values())
        
        productivity_score = (productive_time / total_time * 100) if total_time > 0 else 0
        
        # Generate insights
        insights = []
        if productivity_score > 70:
            insights.append("Excellent productivity! You spent most of your time on productive tasks.")
        elif productivity_score > 40:
            insights.append("Good productivity balance. Consider reducing time on non-productive apps.")
        else:
            insights.append("Low productivity detected. Try to focus more on work-related applications.")
        
        return {
            "score": productivity_score,
            "insights": insights,
            "hourly_data": dict(hourly_data)
        }
    
    def _generate_resource_analysis(self):
        """Analyze system resource usage"""
        if not hasattr(self.data_manager, 'resource_data') or not self.data_manager.resource_data:
            return {"available": False}
        
        resource_data = self.data_manager.resource_data
        
        return {
            "available": True,
            "system": resource_data.get('system', {}),
            "resource_hogs": resource_data.get('resource_hogs', {}),
            "recommendations": self._generate_resource_recommendations(resource_data)
        }
    
    def _generate_resource_recommendations(self, resource_data):
        """Generate resource optimization recommendations"""
        recommendations = []
        
        system = resource_data.get('system', {})
        
        if system.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected. Consider closing unnecessary applications.")
        
        if system.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage. Restart memory-intensive applications.")
        
        if system.get('disk_percent', 0) > 90:
            recommendations.append("Disk space is running low. Clean up temporary files.")
        
        return recommendations
    
    def _generate_timeline_data(self):
        """Generate timeline data for visualization"""
        sessions = self.data_manager.app_sessions
        
        timeline = []
        for session in sessions:
            timeline.append({
                "app": session['app_name'],
                "start": session['start_time'],
                "end": session['end_time'],
                "duration": session['duration_seconds'],
                "active": session['was_active']
            })
        
        return sorted(timeline, key=lambda x: x['start'])
    
    def _generate_html_report(self, report_data):
        """Generate HTML report"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TimeLedger Daily Report - {date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #4CAF50; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: bold; }}
                .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
                .section {{ margin: 30px 0; }}
                .section h2 {{ color: #333; border-left: 4px solid #4CAF50; padding-left: 10px; }}
                .app-list {{ display: grid; gap: 10px; }}
                .app-item {{ display: flex; justify-content: space-between; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
                .timeline {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .insight {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 TimeLedger Daily Report</h1>
                    <p>Report for {date}</p>
                </div>
                
                <div class="summary">
                    <div class="stat-card">
                        <div class="stat-value">{total_hours:.1f}h</div>
                        <div class="stat-label">Total Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{active_hours:.1f}h</div>
                        <div class="stat-label">Active Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{apps_used}</div>
                        <div class="stat-label">Apps Used</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{productivity:.0f}%</div>
                        <div class="stat-label">Productivity</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🏆 Top Applications</h2>
                    <div class="app-list">
                        {app_usage_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Productivity Insights</h2>
                    {productivity_insights_html}
                </div>
                
                <div class="section">
                    <h2>⏰ Activity Timeline</h2>
                    <div class="timeline">
                        <p>Timeline visualization would go here (requires JavaScript charting library)</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>💻 System Performance</h2>
                    {resource_analysis_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        summary = report_data['summary']
        app_usage = report_data['app_usage']
        productivity = report_data['productivity']
        
        # Generate app usage HTML
        app_usage_html = ""
        for app_name, data in list(app_usage.items())[:10]:
            hours = data['total_time'] / 3600
            app_usage_html += f"""
            <div class="app-item">
                <span><strong>{app_name}</strong> ({data['category']})</span>
                <span>{hours:.1f}h ({data['sessions']} sessions)</span>
            </div>
            """
        
        # Generate productivity insights HTML
        productivity_insights_html = ""
        for insight in productivity['insights']:
            productivity_insights_html += f'<div class="insight">{insight}</div>'
        
        # Generate resource analysis HTML
        resource_analysis = report_data['resource_usage']
        if resource_analysis.get('available'):
            resource_analysis_html = "<p>System performance data available in detailed logs.</p>"
        else:
            resource_analysis_html = "<p>No system performance data available for this period.</p>"
        
        return html_template.format(
            date=report_data['date'],
            total_hours=summary['total_time'] / 3600,
            active_hours=summary['active_time'] / 3600,
            apps_used=summary['apps_used'],
            productivity=summary['productivity_ratio'],
            app_usage_html=app_usage_html,
            productivity_insights_html=productivity_insights_html,
            resource_analysis_html=resource_analysis_html
        )

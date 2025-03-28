#!/bin/bash
# social_osint_setup.sh - Setup script for Social Media OSINT tools on Kali Linux

echo "[+] Setting up Social Media OSINT tools for Kali Linux..."

# Update system
echo "[+] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
echo "[+] Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
echo "[+] Creating Python virtual environment..."
mkdir -p ~/social_osint
cd ~/social_osint
python3 -m venv venv
source venv/bin/activate

# Install Sherlock
echo "[+] Installing Sherlock..."
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock
pip install -r requirements.txt
cd ..

# Install Twint
echo "[+] Installing Twint..."
pip install --upgrade -e git+https://github.com/twintproject/twint.git@origin/master#egg=twint

# Install Instaloader
echo "[+] Installing Instaloader..."
pip install instaloader

# Install Social-Analyzer
echo "[+] Installing Social-Analyzer..."
git clone https://github.com/qeeqbox/social-analyzer.git
cd social-analyzer
pip install -r requirements.txt
cd ..

# Install additional dependencies
echo "[+] Installing additional dependencies..."
pip install requests pandas matplotlib seaborn jinja2 pyfiglet colorama

# Create the main script
echo "[+] Creating main script..."
cat > social_media_osint.py << 'EOL'
#!/usr/bin/env python3
"""
Social Media OSINT Tool for Kali Linux - Gathers information about social media accounts
Author: Manus
"""

import os
import sys
import argparse
import subprocess
import json
import time
import re
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama
init(autoreset=True) 

# Global variables
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = SCRIPT_DIR / "results"
SHERLOCK_PATH = SCRIPT_DIR / "sherlock"
SOCIAL_ANALYZER_PATH = SCRIPT_DIR / "social-analyzer"

def print_banner():
    """Print a fancy banner"""
    banner = pyfiglet.figlet_format("Social Media OSINT", font="slant")
    print(f"{Fore.CYAN}{banner}")
    print(f"{Fore.GREEN}A comprehensive OSINT tool for gathering information about social media accounts")
    print(f"{Fore.GREEN}Running on Kali Linux - For ethical use only\n")

def print_status(message, status="info"):
    """Print status messages with color coding"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "info":
        print(f"{Fore.BLUE}[{timestamp}] [INFO] {message}")
    elif status == "success":
        print(f"{Fore.GREEN}[{timestamp}] [SUCCESS] {message}")
    elif status == "warning":
        print(f"{Fore.YELLOW}[{timestamp}] [WARNING] {message}")
    elif status == "error":
        print(f"{Fore.RED}[{timestamp}] [ERROR] {message}")

def ensure_dir(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_status(f"Created directory: {directory}")

def run_command(command, shell=False):
    """Run a shell command and return the output"""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    text=True)
        else:
            process = subprocess.run(command, check=True, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    text=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print_status(f"Command failed: {e}", "error")
        print_status(f"Error output: {e.stderr}", "error")
        return None

def run_sherlock(username, output_dir):
    """Run Sherlock to find username across platforms"""
    print_status(f"Running Sherlock for {username}...")
    
    output_file = os.path.join(output_dir, f"{username}_sherlock.txt")
    output_json = os.path.join(output_dir, f"{username}_sherlock.json")
    
    try:
        # Change to Sherlock directory
        os.chdir(SHERLOCK_PATH)
        
        # Run Sherlock with JSON output
        command = [
            "python3", "sherlock.py", username,
            "--output", output_file,
            "--json", output_json,
            "--timeout", "10"
        ]
        
        result = run_command(command)
        
        # Change back to original directory
        os.chdir(SCRIPT_DIR)
        
        if result:
            print_status(f"Sherlock results saved to {output_file} and {output_json}", "success")
            return True
        return False
    except Exception as e:
        print_status(f"Error running Sherlock: {e}", "error")
        # Change back to original directory
        os.chdir(SCRIPT_DIR)
        return False

def run_twint(username, output_dir):
    """Run Twint to gather Twitter information"""
    print_status(f"Running Twint for Twitter user {username}...")
    
    output_file = os.path.join(output_dir, f"{username}_twitter.json")
    
    try:
        # Basic profile information
        command = [
            "twint", "-u", username,
            "--json", "-o", output_file
        ]
        
        run_command(command)
        print_status(f"Twitter information saved to {output_file}", "success")
        
        # Get followers (limited to 100 to avoid rate limiting)
        followers_file = os.path.join(output_dir, f"{username}_twitter_followers.json")
        command = [
            "twint", "-u", username,
            "--followers", "--limit", "100",
            "--json", "-o", followers_file
        ]
        
        run_command(command)
        print_status(f"Twitter followers saved to {followers_file}", "success")
        
        # Get tweets (limited to 100 to avoid rate limiting)
        tweets_file = os.path.join(output_dir, f"{username}_twitter_tweets.json")
        command = [
            "twint", "-u", username,
            "--limit", "100",
            "--json", "-o", tweets_file
        ]
        
        run_command(command)
        print_status(f"Twitter tweets saved to {tweets_file}", "success")
        
        return True
    except Exception as e:
        print_status(f"Error running Twint: {e}", "error")
        return False

def run_instaloader(username, output_dir):
    """Run Instaloader to gather Instagram information"""
    print_status(f"Running Instaloader for Instagram user {username}...")
    
    try:
        # Create a subdirectory for Instagram data
        insta_dir = os.path.join(output_dir, f"{username}_instagram")
        ensure_dir(insta_dir)
        
        # Run Instaloader
        command = [
            "instaloader",
            "--no-videos",
            "--no-video-thumbnails",
            "--no-captions",
            "--no-compress-json",
            "--dirname-pattern", insta_dir,
            f"profile_{username}"
        ]
        
        run_command(command)
        print_status(f"Instagram information saved to {insta_dir}", "success")
        return True
    except Exception as e:
        print_status(f"Error running Instaloader: {e}", "error")
        return False

def run_social_analyzer(username, output_dir):
    """Run Social-Analyzer to find and analyze profiles"""
    print_status(f"Running Social-Analyzer for {username}...")
    
    output_file = os.path.join(output_dir, f"{username}_social_analyzer.json")
    
    try:
        # Change to Social-Analyzer directory
        os.chdir(SOCIAL_ANALYZER_PATH)
        
        # Run Social-Analyzer
        command = [
            "python3", "app.py",
            "--username", username,
            "--metadata",
            "--output", "json"
        ]
        
        result = run_command(command)
        
        # Change back to original directory
        os.chdir(SCRIPT_DIR)
        
        if result:
            # Save output to file
            with open(output_file, "w") as f:
                f.write(result)
                
            print_status(f"Social-Analyzer results saved to {output_file}", "success")
            return True
        return False
    except Exception as e:
        print_status(f"Error running Social-Analyzer: {e}", "error")
        # Change back to original directory
        os.chdir(SCRIPT_DIR)
        return False

def generate_visualizations(username, output_dir):
    """Generate visualizations from the collected data"""
    print_status(f"Generating visualizations for {username}...")
    
    viz_dir = os.path.join(output_dir, "visualizations")
    ensure_dir(viz_dir)
    
    # Try to read Sherlock results
    try:
        sherlock_json = os.path.join(output_dir, f"{username}_sherlock.json")
        if os.path.exists(sherlock_json):
            with open(sherlock_json, "r") as f:
                sherlock_data = json.load(f)
                
            # Create platform presence visualization
            platforms = []
            found = []
            
            for platform, data in sherlock_data.items():
                platforms.append(platform)
                found.append(1 if data.get("status") == "Claimed" else 0)
            
            if platforms:
                df = pd.DataFrame({"Platform": platforms, "Found": found})
                df = df.sort_values("Found", ascending=False)
                
                plt.figure(figsize=(12, 8))
                sns.barplot(x="Platform", y="Found", data=df)
                plt.xticks(rotation=90)
                plt.title(f"Platform Presence for {username}")
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{username}_platform_presence.png"))
                print_status(f"Platform presence visualization saved to {viz_dir}", "success")
    except Exception as e:
        print_status(f"Error generating Sherlock visualization: {e}", "warning")
    
    # Try to read Twitter results
    try:
        tweets_file = os.path.join(output_dir, f"{username}_twitter_tweets.json")
        if os.path.exists(tweets_file):
            tweets = []
            with open(tweets_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            tweets.append(json.loads(line))
                        except:
                            pass
            
            if tweets:
                # Extract dates and create time series
                dates = []
                for tweet in tweets:
                    try:
                        date = tweet.get("date")
                        if date:
                            dates.append(date)
                    except:
                        pass
                
                if dates:
                    date_counts = {}
                    for date in dates:
                        date = date.split(" ")[0]  # Get just the date part
                        if date in date_counts:
                            date_counts[date] += 1
                        else:
                            date_counts[date] = 1
                    
                    df = pd.DataFrame({"Date": list(date_counts.keys()), "Count": list(date_counts.values())})
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.sort_values("Date")
                    
                    plt.figure(figsize=(12, 6))
                    plt.plot(df["Date"], df["Count"])
                    plt.title(f"Tweet Activity for {username}")
                    plt.xlabel("Date")
                    plt.ylabel("Number of Tweets")
                    plt.tight_layout()
                    plt.savefig(os.path.join(viz_dir, f"{username}_tweet_activity.png"))
                    print_status(f"Tweet activity visualization saved to {viz_dir}", "success")
    except Exception as e:
        print_status(f"Error generating Twitter visualization: {e}", "warning")

def generate_html_report(username, output_dir):
    """Generate an HTML report from all collected data"""
    print_status(f"Generating HTML report for {username}...")
    
    report_file = os.path.join(output_dir, f"{username}_report.html")
    viz_dir = os.path.join(output_dir, "visualizations")
    
    # Basic HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OSINT Report for {username}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
            .platform-found {{ color: green; }}
            .platform-not-found {{ color: red; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OSINT Report for {username}</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    """
    
    # Add Sherlock results
    sherlock_json = os.path.join(output_dir, f"{username}_sherlock.json")
    if os.path.exists(sherlock_json):
        try:
            with open(sherlock_json, "r") as f:
                sherlock_data = json.load(f)
            
            html += """
            <div class="section">
                <h2>Platform Presence (Sherlock Results)</h2>
                <table>
                    <tr>
                        <th>Platform</th>
                        <th>Status</th>
                        <th>URL</th>
                    </tr>
            """
            
            for platform, data in sherlock_data.items():
                status = data.get("status", "Unknown")
                url = data.get("url", "")
                status_class = "platform-found" if status == "Claimed" else "platform-not-found"
                
                html += f"""
                <tr>
                    <td>{platform}</td>
                    <td class="{status_class}">{status}</td>
                    <td><a href="{url}" target="_blank">{url}</a></td>
                </tr>
                """
            
            html += """
                </table>
            </div>
            """
            
            # Add platform presence visualization
            platform_viz = os.path.join(viz_dir, f"{username}_platform_presence.png")
            if os.path.exists(platform_viz):
                # Get relative path
                rel_path = os.path.relpath(platform_viz, output_dir)
                html += f"""
                <div class="section">
                    <h2>Platform Presence Visualization</h2>
                    <img src="{rel_path}" alt="Platform Presence Visualization">
                </div>
                """
        except Exception as e:
            print_status(f"Error adding Sherlock results to report: {e}", "warning")
    
    # Add Twitter results
    tweets_file = os.path.join(output_dir, f"{username}_twitter_tweets.json")
    if os.path.exists(tweets_file):
        try:
            tweets = []
            with open(tweets_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            tweets.append(json.loads(line))
                        except:
                            pass
            
            if tweets:
                # Get user info from first tweet
                user_info = tweets[0].get("user_id", "")
                username = tweets[0].get("username", username)
                name = tweets[0].get("name", "")
                bio = tweets[0].get("bio", "")
                
                html += f"""
                <div class="section">
                    <h2>Twitter Profile</h2>
                    <p><strong>Username:</strong> @{username}</p>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Bio:</strong> {bio}</p>
                    <p><strong>User ID:</strong> {user_info}</p>
                </div>
                """
                
                # Add tweet activity visualization
                tweet_viz = os.path.join(viz_dir, f"{username}_tweet_activity.png")
                if os.path.exists(tweet_viz):
                    # Get relative path
                    rel_path = os.path.relpath(tweet_viz, output_dir)
                    html += f"""
                    <div class="section">
                        <h2>Tweet Activity</h2>
                        <img src="{rel_path}" alt="Tweet Activity Visualization">
                    </div>
                    """
                
                # Add recent tweets
                html += """
                <div class="section">
                    <h2>Recent Tweets</h2>
                    <table>
                        <tr>
                            <th>Date</th>
                            <th>Tweet</th>
                            <th>Likes</th>
                            <th>Retweets</th>
                        </tr>
                """
                
                for i, tweet in enumerate(tweets[:10]):  # Show only first 10 tweets
                    date = tweet.get("date", "")
                    tweet_text = tweet.get("tweet", "")
                    likes = tweet.get("likes_count", 0)
                    retweets = tweet.get("retweets_count", 0)
                    
                    html += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{tweet_text}</td>
                        <td>{likes}</td>
                        <td>{retweets}</td>
                    </tr>
                    """
                
                html += """
                    </table>
                </div>
                """
        except Exception as e:
            print_status(f"Error adding Twitter results to report: {e}", "warning")
    
    # Close HTML
    html += """
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(report_file, "w") as f:
        f.write(html)
    
    print_status(f"HTML report saved to {report_file}", "success")
    return report_file

def generate_report(username, output_dir):
    """Generate a comprehensive report from all tools"""
    print_status(f"Generating comprehensive report for {username}...")
    
    report = {
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platforms": {}
    }
    
    # Try to read Sherlock results
    try:
        sherlock_json = os.path.join(output_dir, f"{username}_sherlock.json")
        if os.path.exists(sherlock_json):
            with open(sherlock_json, "r") as f:
                sherlock_data = json.load(f)
                report["platforms"]["sherlock"] = sherlock_data
    except Exception as e:
        print_status(f"Error reading Sherlock results: {e}", "warning")
    
    # Try to read Twitter results
    try:
        tweets_file = os.path.join(output_dir, f"{username}_twitter_tweets.json")
        if os.path.exists(tweets_file):
            tweets = []
            with open(tweets_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            tweets.append(json.loads(line))
                        except:
                            pass
            
            if tweets:
                report["platforms"]["twitter"] = {
                    "profile_data": tweets[0] if tweets else {},
                    "tweets": tweets
                }
    except Exception as e:
        print_status(f"Error reading Twitter results: {e}", "warning")
    
    # Try to read Social-Analyzer results
    try:
        social_analyzer_file = os.path.join(output_dir, f"{username}_social_analyzer.json")
        if os.path.exists(social_analyzer_file):
            with open(social_analyzer_file, "r") as f:
                social_analyzer_data = json.load(f)
                report["platforms"]["social_analyzer"] = social_analyzer_data
    except Exception as e:
        print_status(f"Error reading Social-Analyzer results: {e}", "warning")
    
    # Save the comprehensive report
    report_file = os.path.join(output_dir, f"{username}_comprehensive_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=4)
    
    print_status(f"Comprehensive report saved to {report_file}", "success")
    
    # Generate HTML report
    html_report = generate_html_report(username, output_dir)
    
    # Generate visualizations
    generate_visualizations(username, output_dir)
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Social Media OSINT Framework for Kali Linux")
    parser.add_argument("username", help="Username to search for")
    parser.add_argument("--twitter", action="store_true", help="Run Twitter analysis")
    parser.add_argument("--instagram", action="store_true", help="Run Instagram analysis")
    parser.add_argument("--all", action="store_true", help="Run all available tools")
    parser.add_argument("--output-dir", help="Custom output directory")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Create results directory
    ensure_dir(RESULTS_DIR)
    
    # Create directory for this search
    if args.output_dir:
        search_dir = Path(args.output_dir)
    else:
        search_dir = RESULTS_DIR / f"{args.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    ensure_dir(search_dir)
    
    print_status(f"Starting OSINT gathering for username: {args.username}")
    print_status(f"Results will be saved to: {search_dir}")
    
    # Always run Sherlock and Social-Analyzer
    sherlock_success = run_sherlock(args.username, search_dir)
    social_analyzer_success = run_social_analyzer(args.username, search_dir)
    
    # Run platform-specific tools if requested
    twitter_success = False
    instagram_success = False
    
    if args.twitter or args.all:
        twitter_success = run_twint(args.username, search_dir)
    
    if args.instagram or args.all:
        instagram_success = run_instaloader(args.username, search_dir)
    
    # Generate comprehensive report
    report = generate_report(args.username, search_dir)
    
    # Summary
    print("\n" + "="*50)
    print_status("OSINT Gathering Summary:", "success")
    print_status(f"Username: {args.username}", "info")
    print_status(f"Sherlock: {'Success' if sherlock_success else 'Failed'}", 
                "success" if sherlock_success else "error")
    print_status(f"Social-Analyzer: {'Success' if social_analyzer_success else 'Failed'}", 
                "success" if social_analyzer_success else "error")
    
    if args.twitter or args.all:
        print_status(f"Twitter Analysis: {'Success' if twitter_success else 'Failed'}", 
                    "success" if twitter_success else "error")
    
    if args.instagram or args.all:
        print_status(f"Instagram Analysis: {'Success' if instagram_success else 'Failed'}", 
                    "success" if instagram_success else "error")
    
    print_status(f"All results saved to: {search_dir}", "success")
    print_status(f"HTML Report: {os.path.join(search_dir, f'{args.username}_report.html')}", "success")
    print("="*50)

if __name__ == "__main__":
    main()
EOL

# Make the script executable
chmod +x social_media_osint.py

echo "[+] Installation complete!"
echo "[+] To run the tool, use: cd ~/social_osint && source venv/bin/activate && python social_media_osint.py <username>"

import requests
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import os

def fetch_github_contributions(username, token):
    """
    Fetch GitHub contribution data for a given username using GraphQL API
    """
    url = "https://api.github.com/graphql"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                            color
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "username": username,
        "from": start_date.isoformat(),
        "to": end_date.isoformat()
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print(f"❌ API Error: {data['errors']}")
            return None
            
        contribution_data = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        print(f"✅ Successfully fetched {contribution_data['totalContributions']} contributions!")
        
        return contribution_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def create_wallpaper(contribution_data, username, width=1920, height=1080):
    """
    Create a wallpaper image from GitHub contribution data
    """
    # Create a new image with dark background
    img = Image.new('RGB', (width, height), color='#0d1117')
    draw = ImageDraw.Draw(img)
    
    # GitHub green color scheme
    colors = {
        0: '#161b22',     # No contributions
        1: '#0e4429',     # Low contributions
        2: '#006d32',     # Medium-low contributions
        3: '#26a641',     # Medium-high contributions
        4: '#39d353'      # High contributions
    }
    
    # Calculate grid dimensions
    weeks = contribution_data['weeks']
    cell_size = 12
    gap = 2
    
    # Calculate starting position to center the grid
    grid_width = len(weeks) * (cell_size + gap) - gap
    grid_height = 7 * (cell_size + gap) - gap
    
    start_x = (width - grid_width) // 2
    start_y = (height - grid_height) // 2 - 50  # Leave space for title
    
    # Draw the contribution grid
    for week_idx, week in enumerate(weeks):
        for day_idx, day in enumerate(week['contributionDays']):
            x = start_x + week_idx * (cell_size + gap)
            y = start_y + day_idx * (cell_size + gap)
            
            # Determine color based on contribution count
            count = day['contributionCount']
            if count == 0:
                color = colors[0]
            elif count <= 2:
                color = colors[1]
            elif count <= 5:
                color = colors[2]
            elif count <= 10:
                color = colors[3]
            else:
                color = colors[4]
            
            # Draw the cell
            draw.rectangle([x, y, x + cell_size, y + cell_size], fill=color)
    
    # Add title
    title_text = f"{username}'s GitHub Contributions"
    try:
        # Try to use a nice font
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Get text dimensions for centering
    bbox = draw.textbbox((0, 0), title_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = start_y - 80
    
    draw.text((text_x, text_y), title_text, fill='#f0f6fc', font=font)
    
    # Add stats
    stats_text = f"Total Contributions: {contribution_data['totalContributions']}"
    try:
        stats_font = ImageFont.truetype("arial.ttf", 18)
    except:
        stats_font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), stats_text, font=stats_font)
    stats_width = bbox[2] - bbox[0]
    stats_x = (width - stats_width) // 2
    stats_y = text_y + 50
    
    draw.text((stats_x, stats_y), stats_text, fill='#7d8590', font=stats_font)
    
    return img

def save_wallpaper(img, filename="github_wallpaper.png"):
    """
    Save the wallpaper image to file
    """
    img.save(filename)
    print(f"✅ Wallpaper saved as {filename}")
    return filename

# Main execution
if __name__ == "__main__":
    # Your credentials
    USERNAME = "username_here"
    TOKEN = "key_here"
    
    print("🚀 Creating your GitHub contribution wallpaper...")
    print("=" * 50)
    
    # Fetch contribution data
    print("1. Fetching GitHub contribution data...")
    contribution_data = fetch_github_contributions(USERNAME, TOKEN)
    
    if not contribution_data:
        print("❌ Failed to fetch contribution data. Exiting.")
        exit(1)
    
    # Create wallpaper
    print("2. Generating wallpaper image...")
    wallpaper_img = create_wallpaper(contribution_data, USERNAME)
    
    # Save wallpaper
    print("3. Saving wallpaper...")
    filename = save_wallpaper(wallpaper_img)
    
    print("=" * 50)
    print(f"🎉 Success! Your GitHub contribution wallpaper has been created!")
    print(f"📁 File saved as: {filename}")
    print(f"📊 Total contributions: {contribution_data['totalContributions']}")
    print(f"🖼️  Resolution: 1920x1080 (Full HD)")
    
    # Open the file location
    print(f"\n💡 You can find your wallpaper at: {os.path.abspath(filename)}")
import ctypes
import os
import schedule
import time
import threading

def set_windows_wallpaper(image_path):
    """
    Set the wallpaper on Windows
    """
    # Get absolute path
    abs_path = os.path.abspath(image_path)
    
    # Windows API call to set wallpaper
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0)
        print(f"✅ Wallpaper set successfully!")
        print(f"📁 Using: {abs_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to set wallpaper: {e}")
        return False

def update_wallpaper():
    """
    Update the GitHub contribution wallpaper
    """
    print(f"\n🔄 Updating wallpaper at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Fetch fresh contribution data
    print("1. Fetching latest GitHub contribution data...")
    contribution_data = fetch_github_contributions(USERNAME, TOKEN)
    
    if not contribution_data:
        print("❌ Failed to fetch contribution data. Skipping update.")
        return
    
    # Create new wallpaper
    print("2. Generating updated wallpaper...")
    wallpaper_img = create_wallpaper(contribution_data, USERNAME)
    
    # Save wallpaper
    print("3. Saving updated wallpaper...")
    filename = save_wallpaper(wallpaper_img)
    
    # Set as desktop wallpaper
    print("4. Setting as desktop wallpaper...")
    set_windows_wallpaper(filename)
    
    print("=" * 50)
    print(f"🎉 Wallpaper updated successfully!")
    print(f"📊 Total contributions: {contribution_data['totalContributions']}")

def start_scheduler():
    """
    Start the background scheduler for automatic updates
    """
    print("\n🤖 Starting automatic wallpaper updater...")
    print("📅 Updates scheduled every 6 hours")
    print("⏰ Press Ctrl+C to stop")
    
    # Schedule updates every 6 hours
    schedule.every(6).hours.do(update_wallpaper)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Update the main execution section
if __name__ == "__main__":
    # Your credentials
    USERNAME = "username_here"
    TOKEN = "key_here"
    
    print("🚀 GitHub Contribution Wallpaper Generator")
    print("=" * 50)
    
    # Ask user what they want to do
    print("Choose an option:")
    print("1. Generate wallpaper once")
    print("2. Generate wallpaper and set as desktop background")
    print("3. Start automatic updates (every 6 hours)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Generate wallpaper once
        print("\n🎨 Generating wallpaper...")
        contribution_data = fetch_github_contributions(USERNAME, TOKEN)
        if contribution_data:
            wallpaper_img = create_wallpaper(contribution_data, USERNAME)
            filename = save_wallpaper(wallpaper_img)
            print(f"✅ Wallpaper saved as: {filename}")
    
    elif choice == "2":
        # Generate and set wallpaper
        print("\n🎨 Generating and setting wallpaper...")
        contribution_data = fetch_github_contributions(USERNAME, TOKEN)
        if contribution_data:
            wallpaper_img = create_wallpaper(contribution_data, USERNAME)
            filename = save_wallpaper(wallpaper_img)
            set_windows_wallpaper(filename)
    
    elif choice == "3":
        # Start automatic updates
        print("\n🎨 Generating initial wallpaper...")
        contribution_data = fetch_github_contributions(USERNAME, TOKEN)
        if contribution_data:
            wallpaper_img = create_wallpaper(contribution_data, USERNAME)
            filename = save_wallpaper(wallpaper_img)
            set_windows_wallpaper(filename)
            
            # Start scheduler
            start_scheduler()
    
    else:
        print("❌ Invalid choice. Please run the script again.")

import json
import asyncio
import argparse
from typing import List, Dict, Any

# Import our content strategy agent
from agents.content_strategy_agent import ContentStrategyAgent, VideoData, ContentAnalysisRequest

async def analyze_videos_from_file(file_path: str) -> Dict[str, Any]:
    """Analyze videos from a JSON file"""
    # Load videos from JSON file
    with open(file_path, 'r') as f:
        video_data = json.load(f)
    
    # Create video objects
    videos = [VideoData(**video) for video in video_data]
    
    # Create request
    request = ContentAnalysisRequest(videos=videos)
    
    # Initialize agent and process request
    agent = ContentStrategyAgent()
    result = await agent.process_request(request)
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Analyze viral short-form videos')
    parser.add_argument('--file', '-f', type=str, help='Path to JSON file containing video data')
    parser.add_argument('--output', '-o', type=str, help='Path to save analysis results (optional)')
    parser.add_argument('--sample', '-s', action='store_true', help='Generate sample video data file')
    
    args = parser.parse_args()
    
    if args.sample:
        # Generate sample video data
        sample_videos = [
            {
                "title": "5 Morning Habits That Changed My Life",
                "description": "I tried these 5 morning habits for 30 days and here's what happened...",
                "views": 1500000,
                "publishedAt": "2023-05-15",
                "channel": "ProductivityGuru"
            },
            {
                "title": "You've Been Charging Your Phone Wrong",
                "description": "This simple trick will make your battery last twice as long!",
                "views": 2300000,
                "publishedAt": "2023-06-02",
                "channel": "TechHacks"
            },
            {
                "title": "What I Eat in a Day as a Nutritionist",
                "description": "Healthy meal ideas that take less than 10 minutes to prepare",
                "views": 950000,
                "publishedAt": "2023-05-28",
                "channel": "HealthyEating"
            },
            {
                "title": "3 Exercises You're Doing Wrong",
                "description": "Fix these common mistakes to prevent injury and get better results",
                "views": 1800000,
                "publishedAt": "2023-06-10",
                "channel": "FitnessExpert"
            },
            {
                "title": "I Tried This Viral Productivity Hack For a Week",
                "description": "The results were shocking...",
                "views": 3200000,
                "publishedAt": "2023-05-20",
                "channel": "LifeHacker"
            }
        ]
        
        sample_file = 'sample_videos.json'
        with open(sample_file, 'w') as f:
            json.dump(sample_videos, f, indent=2)
        
        print(f"Sample video data saved to {sample_file}")
        return
    
    if not args.file:
        print("Please provide a JSON file with video data using --file option")
        print("Or generate a sample file using --sample option")
        return
    
    # Analyze videos
    result = asyncio.run(analyze_videos_from_file(args.file))
    
    # Pretty print the results
    bn formatted_result = json.dumps(result, indent=2)
    print("\n===== CONTENT ANALYSIS RESULTS =====")
    print(formatted_result)
    
    # Save results if output path is provided
    if args.output:
        with open(args.output, 'w') as f:
            f.write(formatted_result)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()

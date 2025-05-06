"""
GitLab Merge Request Manager

This script allows you to:
1. List and sort merge requests by age
2. Close merge requests older than a specified age
3. Generate reports on merge request status

Usage:
    python gitlab_mr_manager.py --token YOUR_TOKEN --project-id YOUR_PROJECT_ID [options]

Options:
    --list                  List all open merge requests sorted by age
    --close-older-than DAYS Close merge requests older than specified days
    --report                Generate a report of merge request statistics
    --dry-run               Show what would be closed without actually closing
    --verbose               Show detailed information

Example:
    python gitlab_mr_manager.py --token glpat-xxxx --project-id 12345 --list
    python gitlab_mr_manager.py --token glpat-xxxx --project-id 12345 --close-older-than 30 --dry-run
"""

import argparse
import datetime
import sys
import requests
import time
from typing import Dict, List, Optional, Tuple
from dateutil.parser import parse as parse_date


class GitLabMRManager:
    """GitLab Merge Request Manager class to handle MR operations"""
    
    def __init__(self, token: str, project_id: str, base_url: str = "https://gitlab.com/api/v4"):
        """Initialize the GitLab MR Manager with authentication details"""
        self.token = token
        self.project_id = project_id
        self.base_url = base_url
        self.headers = {"PRIVATE-TOKEN": token}
    
    def get_merge_requests(self, state: str = "opened") -> List[Dict]:
        """Fetch all merge requests with the specified state"""
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests"
        params = {"state": state, "per_page": 100}
        
        all_mrs = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching merge requests: {response.status_code}")
                print(response.text)
                sys.exit(1)
            
            mrs = response.json()
            if not mrs:
                break
                
            all_mrs.extend(mrs)
            page += 1
        
        return all_mrs
    
    def sort_mrs_by_age(self, mrs: List[Dict]) -> List[Dict]:
        """Sort merge requests by age (oldest first)"""
        return sorted(mrs, key=lambda mr: parse_date(mr["created_at"]))
    
    def calculate_mr_age(self, mr: Dict) -> Tuple[datetime.datetime, int]:
        """Calculate the age of a merge request in days"""
        created_at = parse_date(mr["created_at"])
        now = datetime.datetime.now(created_at.tzinfo)
        age_days = (now - created_at).days
        return created_at, age_days
    
    def close_merge_request(self, mr_iid: int, dry_run: bool = False) -> bool:
        """Close a specific merge request"""
        if dry_run:
            return True
            
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests/{mr_iid}"
        data = {"state_event": "close"}
        
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            print(f"Error closing merge request {mr_iid}: {response.status_code}")
            print(response.text)
            return False
            
        return True
    
    def close_old_merge_requests(self, days: int, dry_run: bool = False, verbose: bool = False) -> Tuple[int, int]:
        """Close merge requests older than the specified number of days"""
        mrs = self.get_merge_requests(state="opened")
        mrs = self.sort_mrs_by_age(mrs)
        
        closed_count = 0
        total_count = len(mrs)
        
        for mr in mrs:
            created_at, age_days = self.calculate_mr_age(mr)
            
            if age_days > days:
                if verbose:
                    print(f"MR #{mr['iid']} '{mr['title']}' is {age_days} days old (created on {created_at.date()})")
                
                action = "Would close" if dry_run else "Closing"
                print(f"{action} MR #{mr['iid']} '{mr['title']}' (age: {age_days} days)")
                
                if self.close_merge_request(mr['iid'], dry_run):
                    closed_count += 1
                    time.sleep(0.5)
            elif verbose:
                print(f"Keeping MR #{mr['iid']} '{mr['title']}' (age: {age_days} days)")
        
        return closed_count, total_count
    
    def list_merge_requests(self, verbose: bool = False) -> None:
        """List all open merge requests sorted by age"""
        mrs = self.get_merge_requests(state="opened")
        mrs = self.sort_mrs_by_age(mrs)
        
        if not mrs:
            print("No open merge requests found.")
            return
            
        print(f"Found {len(mrs)} open merge requests:")
        print("-" * 80)
        
        for mr in mrs:
            created_at, age_days = self.calculate_mr_age(mr)
            author = mr["author"]["name"]
            
            print(f"MR #{mr['iid']} - Age: {age_days} days - Created: {created_at.date()}")
            print(f"Title: {mr['title']}")
            print(f"Author: {author}")
            
            if verbose:
                print(f"URL: {mr['web_url']}")
                print(f"Description: {mr['description'][:100]}..." if mr['description'] else "No description")
                print(f"Branch: {mr['source_branch']} → {mr['target_branch']}")
                
            print("-" * 80)
    
    def generate_report(self) -> None:
        """Generate a report of merge request statistics"""
        open_mrs = self.get_merge_requests(state="opened")
        merged_mrs = self.get_merge_requests(state="merged")
        closed_mrs = self.get_merge_requests(state="closed")
        
        age_buckets = {"<1 week": 0, "1-2 weeks": 0, "2-4 weeks": 0, "1-3 months": 0, ">3 months": 0}
        
        for mr in open_mrs:
            _, age_days = self.calculate_mr_age(mr)
            
            if age_days < 7:
                age_buckets["<1 week"] += 1
            elif age_days < 14:
                age_buckets["1-2 weeks"] += 1
            elif age_days < 30:
                age_buckets["2-4 weeks"] += 1
            elif age_days < 90:
                age_buckets["1-3 months"] += 1
            else:
                age_buckets[">3 months"] += 1
        
        print("\n=== GITLAB MERGE REQUEST REPORT ===\n")
        print(f"Total MRs: {len(open_mrs) + len(merged_mrs) + len(closed_mrs)}")
        print(f"Open MRs: {len(open_mrs)}")
        print(f"Merged MRs: {len(merged_mrs)}")
        print(f"Closed MRs: {len(closed_mrs)}")
        
        print("\nAge Distribution of Open MRs:")
        for bucket, count in age_buckets.items():
            print(f"  {bucket}: {count} MRs")
        
        if open_mrs:
            oldest_mr = self.sort_mrs_by_age(open_mrs)[0]
            _, oldest_age = self.calculate_mr_age(oldest_mr)
            print(f"\nOldest open MR: #{oldest_mr['iid']} '{oldest_mr['title']}' ({oldest_age} days old)")


def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="GitLab Merge Request Manager")
    
    parser.add_argument("--token", required=True, help="GitLab API token")
    parser.add_argument("--project-id", required=True, help="GitLab project ID")
    parser.add_argument("--base-url", default="https://gitlab.com/api/v4", help="GitLab API base URL")
    
    parser.add_argument("--list", action="store_true", help="List all open merge requests sorted by age")
    parser.add_argument("--close-older-than", type=int, help="Close merge requests older than specified days")
    parser.add_argument("--report", action="store_true", help="Generate a report of merge request statistics")
    
    parser.add_argument("--dry-run", action="store_true", help="Show what would be closed without actually closing")
    parser.add_argument("--verbose", action="store_true", help="Show detailed information")
    
    args = parser.parse_args()
    
    manager = GitLabMRManager(args.token, args.project_id, args.base_url)
    
    if args.list:
        manager.list_merge_requests(args.verbose)
    
    if args.close_older_than is not None:
        closed, total = manager.close_old_merge_requests(
            args.close_older_than, args.dry_run, args.verbose
        )
        
        action = "Would close" if args.dry_run else "Closed"
        print(f"\n{action} {closed} out of {total} merge requests older than {args.close_older_than} days.")
    
    if args.report:
        manager.generate_report()
    
    if not (args.list or args.close_older_than is not None or args.report):
        parser.print_help()


if __name__ == "__main__":
    main()

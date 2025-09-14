#!/usr/bin/env python3
"""
Systematic Git Workflow Manager
Provides snapshot and feature branch management for Beast Mode development
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import argparse

class GitWorkflowManager:
    """Systematic Git workflow management"""
    
    def __init__(self):
        self.snapshots_file = ".git/beast_mode_snapshots.json"
        self.load_snapshots()
    
    def load_snapshots(self):
        """Load snapshot metadata"""
        if os.path.exists(self.snapshots_file):
            with open(self.snapshots_file, 'r') as f:
                self.snapshots = json.load(f)
        else:
            self.snapshots = {}
    
    def save_snapshots(self):
        """Save snapshot metadata"""
        with open(self.snapshots_file, 'w') as f:
            json.dump(self.snapshots, f, indent=2)
    
    def run_git(self, cmd: List[str]) -> str:
        """Run git command and return output"""
        try:
            result = subprocess.run(['git'] + cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            print(f"Error output: {e.stderr}")
            sys.exit(1)
    
    def create_snapshot(self, name: str, description: str = ""):
        """Create a systematic snapshot"""
        timestamp = datetime.now().isoformat()
        branch_name = f"snapshot/{name}-{timestamp.replace(':', '-').replace('.', '-')}"
        
        # Stash current changes
        try:
            self.run_git(['stash', 'push', '-m', f'Snapshot: {name}'])
            stashed = True
        except:
            stashed = False
        
        # Create snapshot branch
        self.run_git(['checkout', '-b', branch_name])
        
        # Restore stashed changes if any
        if stashed:
            try:
                self.run_git(['stash', 'pop'])
            except:
                pass
        
        # Add all changes and commit
        self.run_git(['add', '.'])
        commit_msg = f"Snapshot: {name}\n\n{description}\nTimestamp: {timestamp}"
        self.run_git(['commit', '-m', commit_msg])
        
        # Store snapshot metadata
        self.snapshots[name] = {
            'branch': branch_name,
            'timestamp': timestamp,
            'description': description,
            'commit': self.run_git(['rev-parse', 'HEAD'])
        }
        self.save_snapshots()
        
        print(f"✅ Snapshot '{name}' created on branch '{branch_name}'")
        return branch_name
    
    def list_snapshots(self):
        """List all snapshots"""
        if not self.snapshots:
            print("No snapshots found")
            return
        
        print("📸 Available Snapshots:")
        print("-" * 60)
        for name, info in self.snapshots.items():
            print(f"Name: {name}")
            print(f"Branch: {info['branch']}")
            print(f"Created: {info['timestamp']}")
            print(f"Description: {info.get('description', 'No description')}")
            print(f"Commit: {info['commit'][:8]}")
            print("-" * 60)
    
    def restore_snapshot(self, name: str):
        """Restore a snapshot"""
        if name not in self.snapshots:
            print(f"❌ Snapshot '{name}' not found")
            return
        
        snapshot = self.snapshots[name]
        
        # Stash current changes
        try:
            self.run_git(['stash', 'push', '-m', 'Before snapshot restore'])
            print("💾 Current changes stashed")
        except:
            pass
        
        # Checkout snapshot branch
        self.run_git(['checkout', snapshot['branch']])
        print(f"✅ Restored snapshot '{name}' from {snapshot['timestamp']}")
    
    def delete_snapshot(self, name: str, force: bool = False):
        """Delete a snapshot"""
        if name not in self.snapshots:
            print(f"❌ Snapshot '{name}' not found")
            return
        
        if not force:
            response = input(f"Delete snapshot '{name}'? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        
        snapshot = self.snapshots[name]
        
        # Delete branch
        try:
            self.run_git(['branch', '-D', snapshot['branch']])
            print(f"🗑️  Deleted branch '{snapshot['branch']}'")
        except:
            print(f"⚠️  Could not delete branch '{snapshot['branch']}'")
        
        # Remove from metadata
        del self.snapshots[name]
        self.save_snapshots()
        print(f"✅ Snapshot '{name}' deleted")
    
    def create_feature(self, name: str, base: str = "master"):
        """Create a new feature branch"""
        branch_name = f"feature/{name}"
        
        # Stash current changes
        try:
            self.run_git(['stash', 'push', '-m', f'Before feature: {name}'])
            stashed = True
        except:
            stashed = False
        
        # Checkout base and create feature branch
        self.run_git(['checkout', base])
        self.run_git(['pull', 'origin', base])
        self.run_git(['checkout', '-b', branch_name])
        
        # Restore stashed changes if any
        if stashed:
            try:
                self.run_git(['stash', 'pop'])
            except:
                pass
        
        print(f"🚀 Created feature branch '{branch_name}' from '{base}'")
        return branch_name
    
    def list_features(self):
        """List all feature branches"""
        branches = self.run_git(['branch', '-a']).split('\n')
        feature_branches = [b.strip().replace('* ', '') for b in branches if 'feature/' in b]
        
        if not feature_branches:
            print("No feature branches found")
            return
        
        print("🌟 Feature Branches:")
        print("-" * 40)
        for branch in feature_branches:
            current = "* " if branch.startswith('*') else "  "
            clean_branch = branch.replace('* ', '').replace('remotes/origin/', '')
            print(f"{current}{clean_branch}")
    
    def systematic_commit(self, message: str, spec_ref: str = ""):
        """Create a systematic commit with proper formatting"""
        # Stage all changes
        self.run_git(['add', '.'])
        
        # Format commit message
        if spec_ref:
            formatted_message = f"{message}\n\nSpec: {spec_ref}\nTimestamp: {datetime.now().isoformat()}"
        else:
            formatted_message = f"{message}\n\nTimestamp: {datetime.now().isoformat()}"
        
        # Commit
        self.run_git(['commit', '-m', formatted_message])
        print(f"✅ Systematic commit created: {message}")

def main():
    parser = argparse.ArgumentParser(description='Systematic Git Workflow Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Snapshot commands
    snap_parser = subparsers.add_parser('snapshot', help='Snapshot management')
    snap_subparsers = snap_parser.add_subparsers(dest='snap_action')
    
    create_snap = snap_subparsers.add_parser('create', help='Create snapshot')
    create_snap.add_argument('name', help='Snapshot name')
    create_snap.add_argument('--description', '-d', default='', help='Snapshot description')
    
    snap_subparsers.add_parser('list', help='List snapshots')
    
    restore_snap = snap_subparsers.add_parser('restore', help='Restore snapshot')
    restore_snap.add_argument('name', help='Snapshot name')
    
    delete_snap = snap_subparsers.add_parser('delete', help='Delete snapshot')
    delete_snap.add_argument('name', help='Snapshot name')
    delete_snap.add_argument('--force', '-f', action='store_true', help='Force delete')
    
    # Feature commands
    feat_parser = subparsers.add_parser('feature', help='Feature branch management')
    feat_subparsers = feat_parser.add_subparsers(dest='feat_action')
    
    create_feat = feat_subparsers.add_parser('create', help='Create feature branch')
    create_feat.add_argument('name', help='Feature name')
    create_feat.add_argument('--base', '-b', default='master', help='Base branch')
    
    feat_subparsers.add_parser('list', help='List feature branches')
    
    # Commit commands
    commit_parser = subparsers.add_parser('commit', help='Systematic commit')
    commit_parser.add_argument('message', help='Commit message')
    commit_parser.add_argument('--spec', '-s', help='Spec reference')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = GitWorkflowManager()
    
    if args.command == 'snapshot':
        if args.snap_action == 'create':
            manager.create_snapshot(args.name, args.description)
        elif args.snap_action == 'list':
            manager.list_snapshots()
        elif args.snap_action == 'restore':
            manager.restore_snapshot(args.name)
        elif args.snap_action == 'delete':
            manager.delete_snapshot(args.name, args.force)
    
    elif args.command == 'feature':
        if args.feat_action == 'create':
            manager.create_feature(args.name, args.base)
        elif args.feat_action == 'list':
            manager.list_features()
    
    elif args.command == 'commit':
        manager.systematic_commit(args.message, args.spec)

if __name__ == '__main__':
    main()
#!/bin/bash

# Openflow Playground Monitoring Script
# This script helps monitor the deployment and status of Openflow components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
STACK_NAME="openflow-playground"
REGION=$(aws configure get region)

# Function to print colored output
print_status() {
	echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
	echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
	echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
	echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if stack exists
stack_exists() {
	aws cloudformation describe-stacks --stack-name "STACK_NAM"E &>/dev/null
}

# Function to get stack status
get_stack_status() {
	if stack_exists; then
		aws cloudformation describe-stacks --stack-name "STACK_NAM"E --query
		'Stacks[0].StackStatus' --output text
	else
		echo "STACK_NOT_FOUND"
	fi
}

# Function to monitor CloudFormation stack
monitor_stack() {
	print_header "CloudFormation Stack Status"

	if ! stack_exists; then
		print_error "Stack '"STACK_NAME"' does not exist."
		return 1
	fi

	STATUS=$(get_stack_status)
	print_status "Stack Status: "STATU"S"

	case "STATU"S in
	"CREATE_COMPLETE" | "UPDATE_COMPLETE")
		print_status "Stack deployment completed successfully!"
		;;
	"CREATE_IN_PROGRESS" | "UPDATE_IN_PROGRESS")
		print_warning "Stack deployment is in progress..."
		print_status "This may take 15-20 minutes to complete."
		;;
	"CREATE_FAILED" | "UPDATE_FAILED" | "ROLLBACK_COMPLETE")
		print_error "Stack deployment failed!"
		print_status "Check CloudFormation events for details."
		;;
	*)
		print_warning "Stack status: "STATU"S"
		;;
	esac

	# Show recent events
	print_header "Recent Stack Events"
	aws cloudformation describe-stack-events --stack-name "STACK_NAM"E \
		--query
	'StackEvents[0:5].{Time:Timestamp,Status:ResourceStatus,Resource:LogicalResourceId,Reason:ResourceStatusReason}'
	\ 
	--output table
}

# Function to monitor EC2 instances
monitor_instances() {
	print_header "EC2 Instance Status"

	INSTANCES=$(aws ec2 describe-instances \
		--filters "Name=tag:Name,Values=openflow-agent-*" \
		--query 'Reservations[].Instances[]' \
		--output json)

	INSTANCE_COUNT=$(echo ""INSTANCE"S" | jq 'length')
	if [ ""INSTANCE_COUN"T" -eq 0 ]; then
		print_warning "No Openflow agent instances found."
		return
	fi

	echo ""INSTANCE"S" |
		jq -r '.[]
"Instance: \(.InstanceId)
State: \(.State.Name)
Name: \(.Tags[]?
select(.Key=="Name").Value // "N/A")
Private IP: \(.PrivateIpAddress // "N/A")"'

	# Check if instances are running
	RUNNING_COUNT=$(
		echo ""INSTANCE"S"
		jq '[.[]
select(.State.Name=="running")]
length'
	)
	TOTAL_COUNT=$(echo ""INSTANCE"S" | jq 'length')

	if [ ""RUNNING_COUN"T" -eq ""TOTAL_COUN"T" ]; then
		print_status "All instances are running."
	else
		print_warning ""RUNNING_COUNT"/"TOTAL_COUN"T instances are running."
	fi
}

# Function to check EKS cluster
monitor_eks() {
	print_header "EKS Cluster Status"

	# Get data plane key from stack outputs or parameters
	DATA_PLANE_KEY=$(
		aws cloudformation describe-stacks --stack-name "STACK_NAM"E \
			--query 'Stacks[0].Parameters[?ParameterKey==`DataPlaneKey`].ParameterValue' --output
		text 2>/dev/null ||
			echo "unknown"
	)

	CLUSTER_NAME=""DATA_PLANE_KE"Y"

	if aws eks describe-cluster --name ""CLUSTER_NAM"E" &>/dev/null; then
		CLUSTER_STATUS=$(
			aws eks describe-cluster --name ""CLUSTER_NAM"E" --query
			'cluster.status' --output text
		)
		print_status "EKS Cluster '"CLUSTER_NAME"' Status: "CLUSTER_STATU"S"

		if [ ""CLUSTER_STATU"S" = "ACTIVE" ]; then
			print_status "EKS cluster is active and ready."
		else
			print_warning "EKS cluster is not yet active."
		fi
	else
		print_warning "EKS cluster '"CLUSTER_NAME"' not found or not yet created."
	fi
}

# Function to check S3 bucket
monitor_s3() {
	print_header "S3 Bucket Status"

	BUCKET_NAME="byoc-tf-state-"DATA_PLANE_KEY"-"REGIO"N"

	if aws s3 ls "s3://"BUCKET_NAM"E" &>/dev/null; then
		print_status "S3 bucket '"BUCKET_NAME"' exists."

		# Check bucket contents
		OBJECT_COUNT=$(aws s3 ls "s3://"BUCKET_NAM"E" --recursive | wc -l)
		print_status "Bucket contains "OBJECT_COUN"T objects."
	else
		print_warning "S3 bucket '"BUCKET_NAME"' not found."
	fi
}

# Function to check Secrets Manager
monitor_secrets() {
	print_header "Secrets Manager Status"

	SECRET_NAME="snowflake-oauth2-"DATA_PLANE_KE"Y"

	if aws secretsmanager describe-secret --secret-id ""SECRET_NAM"E" &>/dev/null; then
		print_status "OAuth2 secret '"SECRET_NAME"' exists."
	else
		print_warning "OAuth2 secret '"SECRET_NAME"' not found."
	fi
}

# Function to show deployment progress
show_progress() {
	print_header "Deployment Progress"

	STATUS=$(get_stack_status)

	case "STATU"S in
	"CREATE_COMPLETE" | "UPDATE_COMPLETE")
		print_status "✅ Infrastructure deployment completed"
		print_status "✅ EC2 instance created and configured"
		print_status "✅ EKS cluster should be active"
		print_status "✅ Openflow agent should be running"
		print_status ""
		print_status "Next steps:"
		print_status "1. Check Snowflake console for Openflow deployment"
		print_status "2. Verify connectors are available"
		print_status "3. Test data flow connections"
		;;
	"CREATE_IN_PROGRESS" | "UPDATE_IN_PROGRESS")
		print_status "🔄 Infrastructure deployment in progress..."
		print_status "⏳ This typically takes 15-20 minutes"
		print_status "⏳ EC2 instance is setting up Openflow agent"
		print_status "⏳ EKS cluster is being created"
		;;
	"CREATE_FAILED" | "UPDATE_FAILED")
		print_error "❌ Deployment failed!"
		print_status "Check CloudFormation events for error details"
		;;
	*)
		print_warning "⚠️  Unknown deployment status: "STATU"S"
		;;
	esac
}

# Function to show logs (if possible)
show_logs() {
	print_header "Recent Logs"

	if ! stack_exists; then
		print_warning "Stack does not exist. No logs available."
		return
	fi

	# Get instance ID
	INSTANCE_ID=$(
		aws ec2 describe-instances \
			--filters "Name=tag:Name,Values=openflow-agent-*"
		"Name=instance-state-name,Values=running" \
			--query 'Reservations[0].Instances[0].InstanceId' --output text
	)

	if [ ""INSTANCE_I"D" = "None" ] || [ -z ""INSTANCE_I"D" ]; then
		print_warning "No running instances found for log access."
		return
	fi

	print_status "Instance ID: "INSTANCE_I"D"
	print_status "To view logs, you can connect to the instance and check:"
	print_status "  - /var/log/cloud-init-output.log (setup logs)"
	print_status "  - /home/ec2-user/host-scripts/ (agent logs)"
	print_status "  - journalctl -u openflow-setup-agent.service (service logs)"
}

# Function to show all monitoring info
show_all() {
	monitor_stack
	echo ""
	monitor_instances
	echo ""
	monitor_eks
	echo ""
	monitor_s3
	echo ""
	monitor_secrets
	echo ""
	show_progress
	echo ""
	show_logs
}

# Main script logic
main() {
	case "${1:-all}" in
	"stack")
		monitor_stack
		;;
	"instances")
		monitor_instances
		;;
	"eks")
		monitor_eks
		;;
	"s3")
		monitor_s3
		;;
	"secrets")
		monitor_secrets
		;;
	"progress")
		show_progress
		;;
	"logs")
		show_logs
		;;
	"all")
		show_all
		;;
	"help" | "-h" | "--help")
		echo "Usage: $0 [command]"
		echo ""
		echo "Commands:"
		echo "  all       - Show all monitoring information (default)"
		echo "  stack     - Monitor CloudFormation stack"
		echo "  instances - Monitor EC2 instances"
		echo "  eks       - Monitor EKS cluster"
		echo "  s3        - Monitor S3 bucket"
		echo "  secrets   - Monitor Secrets Manager"
		echo "  progress  - Show deployment progress"
		echo "  logs      - Show log information"
		echo "  help      - Show this help message"
		;;
	*)
		print_error "Unknown command: $1"
		echo "Use '$0 help' for usage information."
		exit 1
		;;
	esac
}

# Run main function with all arguments
main "$@"

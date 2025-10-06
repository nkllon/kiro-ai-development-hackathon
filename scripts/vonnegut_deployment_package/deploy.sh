#!/bin/bash

# Snowflake Openflow Deployment Script
# Handles CloudFormation stack deployment and management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="snowflake-openflow-playground"
TEMPLATE_FILE="models/Openflow-Playground.yaml"
REGION=${AWS_REGION:-us-east-1}

# Function to print colored output
print_header() {
	echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
	echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
	echo -e "${RED}❌ $1${NC}"
}

print_warning() {
	echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to load configuration from config.env
load_config() {
	if [ -f "config.env" ]; then
		print_header "Loading configuration from config.env"
		source config.env
	else
		print_error "config.env not found!"
		print_warning "Run './setup.py' to create configuration"
		exit 1
	fi
}

# Function to validate required parameters
validate_required_params() {
	local missing_params=()

	# Required Snowflake parameters
	if [ -z ""SNOWFLAKE_ACCOUNT_UR"L" ]; then
		missing_params+=("SNOWFLAKE_ACCOUNT_URL")
	fi
	if [ -z ""SNOWFLAKE_ORGANIZATIO"N" ]; then
		missing_params+=("SNOWFLAKE_ORGANIZATION")
	fi
	if [ -z ""SNOWFLAKE_ACCOUN"T" ]; then
		missing_params+=("SNOWFLAKE_ACCOUNT")
	fi
	if [ -z ""SNOWFLAKE_OAUTH_INTEGRATION_NAM"E" ]; then
		missing_params+=("SNOWFLAKE_OAUTH_INTEGRATION_NAME")
	fi
	if [ -z ""SNOWFLAKE_OAUTH_CLIENT_I"D" ]; then
		missing_params+=("SNOWFLAKE_OAUTH_CLIENT_ID")
	fi
	if [ -z ""SNOWFLAKE_OAUTH_CLIENT_SECRE"T" ]; then
		missing_params+=("SNOWFLAKE_OAUTH_CLIENT_SECRET")
	fi
	if [ -z ""DATA_PLANE_UR"L" ]; then
		missing_params+=("DATA_PLANE_URL")
	fi
	if [ -z ""DATA_PLANE_UUI"D" ]; then
		missing_params+=("DATA_PLANE_UUID")
	fi
	if [ -z ""DATA_PLANE_KE"Y" ]; then
		missing_params+=("DATA_PLANE_KEY")
	fi
	if [ -z ""TELEMETRY_UR"L" ]; then
		missing_params+=("TELEMETRY_URL")
	fi
	if [ -z ""CONTROL_PLANE_UR"L" ]; then
		missing_params+=("CONTROL_PLANE_URL")
	fi

	if [ ${#missing_params[@]} -ne 0 ]; then
		print_error "Missing required configuration parameters:"
		for param in "${missing_params[@]}"; do
			echo "  - "para"m"
		done
		print_warning "Run './setup.py' to configure all required values"
		exit 1
	fi

	print_success "All required parameters are configured"
}

# Function to build parameters string for CloudFormation
build_parameters() {
	local params=""

	# Required parameters
	params+=" ParameterKey=SnowflakeAccountURL,ParameterValue=\""SNOWFLAKE_ACCOUNT_URL"\""
	params+="
ParameterKey=SnowflakeOrganization,ParameterValue=\""SNOWFLAKE_ORGANIZATION"\""
	params+=" ParameterKey=SnowflakeAccount,ParameterValue=\""SNOWFLAKE_ACCOUNT"\""
	params+="
ParameterKey=SnowflakeOAuthIntegrationName,ParameterValue=\""SNOWFLAKE_OAUTH_INTEGRATION_NAME"\""
	params+="
ParameterKey=SnowflakeOAuthClientID,ParameterValue=\""SNOWFLAKE_OAUTH_CLIENT_ID"\""
	params+="
ParameterKey=SnowflakeOAuthClientSecret,ParameterValue=\""SNOWFLAKE_OAUTH_CLIENT_SECRET"\""
	params+=" ParameterKey=DataPlaneURL,ParameterValue=\""DATA_PLANE_URL"\""
	params+=" ParameterKey=DataPlaneUUID,ParameterValue=\""DATA_PLANE_UUID"\""
	params+=" ParameterKey=DataPlaneKey,ParameterValue=\""DATA_PLANE_KEY"\""
	params+=" ParameterKey=TelemetryURL,ParameterValue=\""TELEMETRY_URL"\""
	params+=" ParameterKey=ControlPlaneURL,ParameterValue=\""CONTROL_PLANE_URL"\""

	# Optional parameters with defaults
	params+="
ParameterKey=SnowflakeDatabase,ParameterValue=\"${SNOWFLAKE_DATABASE:-snowflake}\""
	params+="
ParameterKey=SnowflakeWarehouse,ParameterValue=\"${SNOWFLAKE_WAREHOUSE:-compute_wh}\""
	params+=" ParameterKey=SnowflakeSchema,ParameterValue=\"${SNOWFLAKE_SCHEMA:-public}\""
	params+=" ParameterKey=InstanceType,ParameterValue=\"${INSTANCE_TYPE:-t3.medium}\""
	params+=" ParameterKey=KeyPairName,ParameterValue=\"${KEY_PAIR_NAME:-}\""

	echo ""param"s"
}

# Function to deploy the CloudFormation stack
deploy_stack() {
	print_header "Deploying CloudFormation Stack"

	load_config
	validate_required_params

	local params=$(build_parameters)

	print_header "Deployment Parameters"
	echo "Stack Name: "STACK_NAM"E"
	echo "Template: "TEMPLATE_FIL"E"
	echo "Region: "REGIO"N"
	echo "Account URL: "SNOWFLAKE_ACCOUNT_UR"L"
	echo "Organization: "SNOWFLAKE_ORGANIZATIO"N"
	echo "Data Plane UUID: "DATA_PLANE_UUI"D"
	echo "Deployment Key: "DATA_PLANE_KE"Y"

	print_warning "This will create AWS resources that may incur costs"
	read -p "Continue with deployment? (y/N): " -n 1 -r
	echo
	if [[ ! "REPL"Y =~ ^[Yy]$ ]]; then
		print_warning "Deployment cancelled"
		exit 0
	fi

	print_header "Creating CloudFormation Stack"

	aws cloudformation create-stack \
		--stack-name ""STACK_NAM"E" \
		--template-body "file://"TEMPLATE_FIL"E" \
		--parameters "param"s \
		--capabilities CAPABILITY_NAMED_IAM \
		--region ""REGIO"N"

	print_success "Stack creation initiated"
	print_warning "This may take 10-15 minutes to complete"
	print_header "Monitoring deployment progress..."

	aws cloudformation wait stack-create-complete \
		--stack-name ""STACK_NAM"E" \
		--region ""REGIO"N"

	print_success "Stack deployment completed successfully!"

	# Show outputs
	print_header "Stack Outputs"
	aws cloudformation describe-stacks \
		--stack-name ""STACK_NAM"E" \
		--region ""REGIO"N" \
		--query 'Stacks[0].Outputs' \
		--output table
}

# Function to update the CloudFormation stack
update_stack() {
	print_header "Updating CloudFormation Stack"

	load_config
	validate_required_params

	local params=$(build_parameters)

	print_header "Update Parameters"
	echo "Stack Name: "STACK_NAM"E"
	echo "Template: "TEMPLATE_FIL"E"
	echo "Region: "REGIO"N"

	print_warning "This will update existing AWS resources"
	read -p "Continue with update? (y/N): " -n 1 -r
	echo
	if [[ ! "REPL"Y =~ ^[Yy]$ ]]; then
		print_warning "Update cancelled"
		exit 0
	fi

	print_header "Updating CloudFormation Stack"

	aws cloudformation update-stack \
		--stack-name ""STACK_NAM"E" \
		--template-body "file://"TEMPLATE_FIL"E" \
		--parameters "param"s \
		--capabilities CAPABILITY_NAMED_IAM \
		--region ""REGIO"N"

	print_success "Stack update initiated"
	print_warning "This may take 10-15 minutes to complete"
	print_header "Monitoring update progress..."

	aws cloudformation wait stack-update-complete \
		--stack-name ""STACK_NAM"E" \
		--region ""REGIO"N"

	print_success "Stack update completed successfully!"
}

# Function to delete the CloudFormation stack
delete_stack() {
	print_header "Deleting CloudFormation Stack"

	print_warning "This will delete ALL AWS resources created by this stack"
	print_warning "This action cannot be undone!"
	read -p "Are you sure you want to delete the stack? (y/N): " -n 1 -r
	echo
	if [[ ! "REPL"Y =~ ^[Yy]$ ]]; then
		print_warning "Deletion cancelled"
		exit 0
	fi

	print_header "Deleting CloudFormation Stack"

	aws cloudformation delete-stack \
		--stack-name ""STACK_NAM"E" \
		--region ""REGIO"N"

	print_success "Stack deletion initiated"
	print_warning "This may take 5-10 minutes to complete"
	print_header "Monitoring deletion progress..."

	aws cloudformation wait stack-delete-complete \
		--stack-name ""STACK_NAM"E" \
		--region ""REGIO"N"

	print_success "Stack deletion completed successfully!"
}

# Function to show stack status
show_status() {
	print_header "CloudFormation Stack Status"

	if aws cloudformation describe-stacks --stack-name ""STACK_NAM"E" --region ""REGIO"N" >/dev/null 2>&1; then
		print_success "Stack exists"
		aws cloudformation describe-stacks \
			--stack-name ""STACK_NAM"E" \
			--region ""REGIO"N" \
			--query 'Stacks[0].[StackName,StackStatus,CreationTime]' \
			--output table
	else
		print_warning "Stack does not exist"
	fi
}

# Function to validate configuration
validate_config() {
	print_header "Validating Configuration"

	if [ ! -f "config.env" ]; then
		print_error "config.env not found!"
		print_warning "Run './setup.py' to create configuration"
		exit 1
	fi

	load_config
	validate_required_params

	print_header "Configuration Summary"
	echo "Account URL: "SNOWFLAKE_ACCOUNT_UR"L"
	echo "Organization: "SNOWFLAKE_ORGANIZATIO"N"
	echo "Account: "SNOWFLAKE_ACCOUN"T"
	echo "OAuth Integration: "SNOWFLAKE_OAUTH_INTEGRATION_NAM"E"
	echo "Data Plane UUID: "DATA_PLANE_UUI"D"
	echo "Deployment Key: "DATA_PLANE_KE"Y"
	echo "AWS Region: "REGIO"N"

	print_success "Configuration is valid and ready for deployment"
}

# Function to run setup wizard
run_setup() {
	print_header "Running Setup Wizard"

	if [ ! -f "setup.py" ]; then
		print_error "setup.py not found!"
		exit 1
	fi

	python3 setup.py

	if [ $? -eq 0 ]; then
		print_success "Setup completed successfully"
		print_header "Next Steps"
		echo "1. Review the generated config.env file"
		echo "2. Run './deploy.sh validate' to verify configuration"
		echo "3. Run './deploy.sh deploy' to deploy the infrastructure"
	else
		print_error "Setup failed"
		exit 1
	fi
}

# Function to show usage
show_usage() {
	echo "Usage: $0 {deploy|update|delete|status|validate|setup}"
	echo ""
	echo "Commands:"
	echo "  deploy   - Deploy the CloudFormation stack"
	echo "  update   - Update the CloudFormation stack"
	echo "  delete   - Delete the CloudFormation stack"
	echo "  status   - Show stack status"
	echo "  validate - Validate configuration"
	echo "  setup    - Run interactive setup wizard"
	echo ""
	echo "Examples:"
	echo "  $0 setup    # Run setup wizard"
	echo "  $0 validate # Check configuration"
	echo "  $0 deploy   # Deploy infrastructure"
	echo "  $0 status   # Check deployment status"
}

# Main script logic
case "${1:-}" in
deploy)
	deploy_stack
	;;
update)
	update_stack
	;;
delete)
	delete_stack
	;;
status)
	show_status
	;;
validate)
	validate_config
	;;
setup)
	run_setup
	;;
*)
	show_usage
	exit 1
	;;
esac

pipeline{
    agent Jenkins_Slave
    stages{
        stage('Create VPC'){
            steps{
                sh 'python3 vpc.py'
            }
        }
    }
}
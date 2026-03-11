def OLD_KNOWLEDGE
def NEW_KNOWLEDGE

pipeline {
   agent {
     docker {
       image 'alpine:latest'
       label 'Wrangler1'
       args  '-v /tmp:/tmp -u0'
     }
   }
  environment {
    AI_URL="https://ai.hackedyour.info"
    NEW_KNOWLEDGE = "72ed66da-d9ff-4e70-b803-d7dadc11e2ae"
    AI_KEY = credentials('ai-hacked-your-info-key')
    ACCEPTJSON="accept: application/json"
    CONTENTJSON="Content-Type: application/json"
    BASE="${AI_URL}/api/v1"
    FILE_EP="${BASE}/knowledge/${CVKNOWLEDGE}/file/add"
    AUTHBEARER="Authorization: Bearer ${AI_KEY}"
    BOTNAME="[Bot Name]"
    KNOWLEDGENAME="CV for [Your Name]"
    DESCRIPTION="[Your Name]s CV docs"

  }

  stages {
    stage('Setup container'){
      steps{
        script{
          //add the tools
          sh """#! /bin/sh\n
          apk update;\n
          apk add --no-cache git curl bash jq;"""
        }
      }
    }
    stage('gather content'){
      steps {
        dir('Cv') {
          git branch: 'main', 
              credentialsId: '[git-credentials-id]', 
              url: 'https://github.com/[Username]/Cv.git'
        }
      }
    }
    stage('Find old repo') {
      steps {
        script {
          // curl -H "${AUTHBEARER}" -H "${ACCEPTJSON}" "${BASE}/models/model?id=${BOTNAME}"
          OLD_KNOWLEDGE=sh (script: """
          #!/bin/sh
          /usr/bin/curl -s -H "${AUTHBEARER}" -H "${ACCEPTJSON}" "${BASE}/models/model?id=${BOTNAME}" | /usr/bin/jq -r .meta.knowledge[0].id
          """, returnStdout: true).trim()
        }
      }
    }
    
    stage('Create New Repo'){
      steps {
        script {

          def date = sh (script: 'date +"%F-%H:%M"', returnStdout: true).trim()

          sh("""
              #!/bin/sh
              jq -n -c --arg name "${KNOWLEDGENAME}@${date}" --arg description "${DESCRIPTION}" \
              '{ "name": \$name, "description": \$description, "data": {}, "access_control": null }' >create_repo.json;
              cat create_repo.json
          """)

          NEW_KNOWLEDGE=sh(script: "curl -s -X POST -H \"${AUTHBEARER}\" -H \"${ACCEPTJSON}\" -H \"${CONTENTJSON}\" -d \"@create_repo.json\" ${BASE}/knowledge/create | jq -r .id", returnStdout: true).trim()
          echo "old knowledge ${OLD_KNOWLEDGE}"
          echo "new knowlege ${NEW_KNOWLEDGE}"

        }
      }
    }
    
    stage('Add Files') {
      steps {
        script {
          withEnv(["NEW_KNOWLEDGE=${NEW_KNOWLEDGE}"]) {

            sh '''
              cd Cv
            
              # Recursively find all markdown files in the cv-data directory
              find cv-data -name "*.md" -print0 | while IFS= read -r -d '' file; do
                # Strip leading ./ for clean path
                file_path="${file#./}"

                # Exclusion 1: Skip files containing NORAG in the name
                if [[ "$file_path" == *"-NORAG.md" ]]; then
                    echo "Skipping NORAG file: $file_path"
                    continue
                fi

                # Exclusion 2: Skip files in cv-data/resumes/ directory
                if [[ "$file_path" == "cv-data/resumes/"* ]]; then
                    echo "Skipping resume file: $file_path"
                    continue
                fi

                echo "Uploading $file_path"
                response=$(curl -s -X POST -H "$AUTHBEARER" -H "$ACCEPTJSON" \
                    -F "file=@$file_path;filename=$(basename "$file_path");type=text/plain" \
                    "$BASE/files/")

                fileId=$(echo "$response" | jq -r .id)

                if [ "$fileId" != "null" ]; then
                    echo "linking ${file_path}"
                    # Generate the JSON payload using jq to guarantee proper quoting
                    JSON_PAYLOAD=$(jq -n --arg id "$fileId" '{"file_id": $id}')
                    
                    curl --fail-with-body -sS --retry 3 --retry-delay 2 \
                      -o >(cat >&2) \
                      -H "${AUTHBEARER}" \
                      -H "${CONTENTJSON}" \
                      --data "$JSON_PAYLOAD" \
                      "${BASE}/knowledge/${NEW_KNOWLEDGE}/file/add"
                else 
                    echo "could not process file"
                fi
              done
               
            '''
          }
        }
      }
    }
    stage ("Attach Knowledge"){
      steps {
        script {
          withEnv(["NEW_KNOWLEDGE=${NEW_KNOWLEDGE}"]) {
            sh '''
              set -euo pipefail
                curl -sf -H "$ACCEPTJSON" -H "Authorization: Bearer $AI_KEY" "$BASE/knowledge/" | \
                jq --arg id "$NEW_KNOWLEDGE" '(.[] | select(.id==$id)) + {type:"collection"}' > collection.json
            '''
          }

          sh 'set -euo pipefail; curl -sf -H "$ACCEPTJSON" -H "Authorization: Bearer $AI_KEY" "$BASE/models/model?id=$BOTNAME" > model.json'
          sh 'jq ".meta.knowledge=[]" model.json > no_knowledge_model.json'
          sh 'curl -sfX POST -H "$ACCEPTJSON" -H "$CONTENTJSON" -H "Authorization: Bearer $AI_KEY" --data-binary @no_knowledge_model.json "$BASE/models/model/update?id=$BOTNAME"'
                    
        
          sh """
            jq --slurpfile knowledge collection.json '.meta.knowledge = \$knowledge' \
                 no_knowledge_model.json > new_model.json
                 """


          sh 'curl -sfX POST -H "$ACCEPTJSON" -H "$CONTENTJSON" -H "Authorization: Bearer $AI_KEY" --data-binary @new_model.json "$BASE/models/model/update?id=$BOTNAME"'
        }
      }
    }

    stage ("Delete Old Knowledge"){
      steps {
        script {
          withEnv(["OLD_KNOWLEDGE=${OLD_KNOWLEDGE}"]) {
            sh 'curl -sfX DELETE -H "$ACCEPTJSON" -H "$AUTHBEARER" "$BASE/knowledge/$OLD_KNOWLEDGE/delete"'
          }
        }
      }
    }
  }
}

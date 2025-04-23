# NeoTaxi
Please follow these steps to run this project: 
1. Start minikube with additional resources:
```
minikube start --memory=6000 --cpus=6
```

2. After completing all the steps outlined in grader.md, ensure all pods and services are created and running:
```
kubectl get pods
```
```
kubectl get services
```


3. Once all pods are running, forward the four required ports. Use two separate terminal windows and execute the following commands:
```
kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
kubectl port-forward svc/kafka-service 9092:9092 29092:29092
```

4. Start the Data Producer: Execute the following command to begin streaming data into Kafka:
```
python3 data_producer.py
```

5. Run the Tester Script: After the data producer script (data_producer.py) finishes streaming data into Kafka, run the tester.py script:
```
python3 tester.py
```

Note: Use the interface.py file provided in the ZIP folder submitted on canvas (also committed to this branch) to test this project. This version of interface.py includes updates that differ from the version submitted in Phase 1.


Steps to troubleshoot if data is not being inserted into neo4j:

Scale down the connector pod:
```
kubectl scale deployment kafka-neo4j-connector --replicas=0
```

Exec into the kafka deployment pod:
```
kubectl exec -it <kafka-pd-name> -- /bin/bash
```

Delete and re-create kafka topic:
```
/bin/kafka-topics --bootstrap-server localhost:29092 --delete --topic nyc_taxicab_data
```
```
/bin/kafka-topics --bootstrap-server localhost:29092 --create --topic nyc_taxicab_data --partitions 3 --replication-factor 1
```

Sometimes this works too: 
Updating Topic Retention Policy
```
/bin/kafka-configs --bootstrap-server localhost:29092 --entity-type topics --entity-name nyc_taxicab_data --alter --add-config retention.ms=1000
```

Verify Retention Policy
```
/bin/kafka-configs --bootstrap-server localhost:29092 --entity-type topics --entity-name nyc_taxicab_data --describe
```

Restoring default Retention Policy
```
/bin/kafka-configs --bootstrap-server localhost:29092 --entity-type topics --entity-name nyc_taxicab_data --alter --add-config retention.ms=604800000
```

TO check if data is getting streamed into kafka:
```
/bin/kafka-console-consumer --bootstrap-server localhost:29092 --topic nyc_taxicab_data --from-beginning
```

Scale up the pod:
```
kubectl scale deployment kafka-neo4j-connector --replicas=1
```



Cypher queries:
To delete already present nodes from neo4j run the below cypher-query:
```
MATCH (n) DETACH DELETE n;
```

To visualize: 
```
CALL db.schema.visualization();
```


To check number of nodes:
```
MATCH (n) RETURN COUNT(n) AS total_nodes;
```

To check number of edges:
```
MATCH ()-[r]->() RETURN count(r) AS numberOfRelationships;
```

To verify gds installation: 
```
Return gds.version();
```
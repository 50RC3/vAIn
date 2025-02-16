# vAIn API Reference

## Overview
vAIn provides a RESTful API and WebSocket service for managing AGI tasks, monitoring system performance, and handling real-time data updates. Below is the API reference for all available endpoints and events.

---

## Table of Contents
1. [Authentication](#authentication)
2. [Core APIs](#core-apis)
   - [Node Management](#node-management)
     - [GET /api/v1/nodes](#get-apiv1nodes)
   - [Federated Learning](#federated-learning)
     - [POST /api/v1/fl/round/start](#post-apiv1flroundstart)
     - [POST /api/v1/fl/round/{round_id}/update](#post-apiv1flroundround_idupdate)
   - [Meta-Learning](#meta-learning)
     - [GET /api/v1/meta/tasks](#get-apiv1metatasks)
     - [POST /api/v1/meta/transfer](#post-apiv1metatransfer)
   - [Neural Architecture Search](#neural-architecture-search)
     - [POST /api/v1/nas/evolve](#post-apiv1nasevolve)
3. [Task API](#task-api)
   - [GET /tasks](#get-tasks)
   - [POST /tasks](#post-tasks)
   - [GET /tasks/{task_id}](#get-task-id)
   - [PUT /tasks/{task_id}](#put-task-id)
4. [Performance API](#performance-api)
   - [GET /performance](#get-performance)
5. [Visualization API](#visualization-api)
   - [GET /visualizations](#get-visualizations)
6. [WebSocket Service](#websocket-service)
   - [ws://localhost/ws/tasks](#ws-tasks)
7. [Notification System](#notification-system)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Version History](#version-history)

---

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```http
Authorization: Bearer <token>
```

## Core APIs

### Node Management
#### GET /api/v1/nodes
Get list of active nodes in the network.
```json
{
  "nodes": [
    {
      "node_id": "compute-01",
      "type": "COMPUTE",
      "status": "active",
      "resources": {
        "cpu_cores": 8,
        "memory": 16384,
        "gpu": true
      },
      "trust_score": 0.95
    }
  ]
}
```

### Federated Learning
#### POST /api/v1/fl/round/start
Start a new federated learning round.
```json
{
  "round_id": "r123",
  "min_nodes": 3,
  "model_hash": "Qm...",
  "aggregation_method": "fedavg"
}
```

#### POST /api/v1/fl/round/{round_id}/update
Submit model updates for a round.
```json
{
  "node_id": "compute-01",
  "weights_hash": "Qm...",
  "metrics": {
    "loss": 0.123,
    "accuracy": 0.95
  }
}
```

### Meta-Learning
#### GET /api/v1/meta/tasks
Get available meta-learning tasks.

#### POST /api/v1/meta/transfer
Request knowledge transfer between domains.
```json
{
  "source_domain": "vision",
  "target_domain": "nlp",
  "transfer_method": "maml"
}
```

### Neural Architecture Search
#### POST /api/v1/nas/evolve
Trigger architecture evolution.
```json
{
  "population_size": 100,
  "generations": 50,
  "fitness_metric": "accuracy/compute"
}
```

## Task API

### GET /tasks
Retrieve a list of all tasks.

#### Response
- **200 OK**: Returns a list of tasks.
```json
[
  {
    "task_id": 1,
    "name": "Task 1",
    "status": "completed",
    "priority": "high",
    "created_at": "2024-11-18T10:00:00Z"
  },
  {
    "task_id": 2,
    "name": "Task 2",
    "status": "in-progress",
    "priority": "medium",
    "created_at": "2024-11-18T10:30:00Z"
  }
]
```

## WebSocket Service

### Connection
```javascript
const ws = new WebSocket('ws://localhost/ws/events');
```

### Event Types
```typescript
interface Event {
  type: 'FL_ROUND_UPDATE' | 'NODE_STATUS' | 'PERFORMANCE_METRIC' | 'ERROR';
  payload: any;
}
```

#### Federated Learning Events
```json
{
  "type": "FL_ROUND_UPDATE",
  "payload": {
    "round_id": "r123",
    "status": "aggregating",
    "participants": 5,
    "current_loss": 0.123
  }
}
```

#### Node Status Events
```json
{
  "type": "NODE_STATUS",
  "payload": {
    "node_id": "compute-01",
    "status": "training",
    "resource_usage": {
      "cpu": 85,
      "memory": 7168,
      "gpu": 90
    }
  }
}
```

## Error Handling
All endpoints use standard HTTP status codes and return errors in the format:
```json
{
  "error": {
    "code": "INVALID_MODEL_UPDATE",
    "message": "Model update verification failed",
    "details": {
      "round_id": "r123",
      "reason": "signature_mismatch"
    }
  }
}
```

## Rate Limiting
- 100 requests per minute for REST APIs
- 10 WebSocket messages per second per connection

## Version History
- v1 (Current): Initial AGI system API
- v0.5 (Deprecated): Beta testing API

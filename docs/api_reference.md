# vAIn API Reference

## Overview
vAIn provides a RESTful API and WebSocket service for managing AGI tasks, monitoring system performance, and handling real-time data updates. Below is the API reference for all available endpoints and events.

---

## Table of Contents
1. [Task API](#task-api)
   - [GET /tasks](#get-tasks)
   - [POST /tasks](#post-tasks)
   - [GET /tasks/{task_id}](#get-task-id)
   - [PUT /tasks/{task_id}](#put-task-id)
2. [Performance API](#performance-api)
   - [GET /performance](#get-performance)
3. [Visualization API](#visualization-api)
   - [GET /visualizations](#get-visualizations)
4. [WebSocket Service](#websocket-service)
   - [ws://localhost/ws/tasks](#ws-tasks)
5. [Notification System](#notification-system)

---

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

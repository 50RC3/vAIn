# Developer Notes for vAIn

This document outlines important notes, design decisions, and development guidelines for vAIn, a versatile real-time task and performance monitoring platform. This is intended to provide insights into the architecture, key features, and best practices used in the development of the platform.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [API Design](#api-design)
- [WebSocket Implementation](#websocket-implementation)
- [Visualization and Performance Monitoring](#visualization-and-performance-monitoring)
- [Notification System](#notification-system)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

---

## Overview

vAIn is designed to manage tasks, monitor system performance, visualize trends, and provide real-time notifications and updates. It supports a RESTful API for CRUD operations on tasks and performance data, WebSocket connections for real-time updates, and dynamic visualization tools. The system integrates multiple components to offer seamless task management, performance tracking, and alerting.

## Architecture

vAIn follows a modular design, separating concerns between task management, system performance monitoring, real-time updates, and data visualization. Below is a breakdown of the major components:

### 1. **Task Management API**
- **Endpoints**: The task management API offers endpoints to create, retrieve, update, and delete tasks.
- **Data Model**: Tasks have attributes like `name`, `status`, `priority`, and `created_at`. Status values can be "pending", "in-progress", or "completed".
  
### 2. **Performance Monitoring**
- **Metrics Tracked**: The performance API tracks system metrics such as CPU usage, memory usage, disk space, and uptime.
- **Data Flow**: These metrics are gathered in real-time and provided through the `/performance` endpoint for frontend consumption.

### 3. **Real-Time Updates (WebSocket)**
- **WebSocket Endpoint**: `ws://localhost/ws/tasks` is used for streaming task updates and system performance changes.
- **Event Types**: Task updates and performance visualizations are sent as events to WebSocket clients.
  
### 4. **Visualization API**
- Provides real-time data for charts, graphs, and trends.
- Example: Visualizes task completion rates, system performance trends over time, etc.

### 5. **Notification System**
- Uses WebSockets to send event-driven notifications for task updates, system warnings, or error events.

---

## Key Features

- **Real-Time Monitoring**: Continuous monitoring of task status and system performance via WebSocket.
- **Task Management**: CRUD operations for task management (create, retrieve, update, delete).
- **Performance Metrics**: Tracks key system performance indicators (CPU, memory, disk, uptime).
- **Visualization**: Dynamic graph and chart generation for task completion and system performance trends.
- **Notifications**: Event-driven notifications delivered via WebSocket for task changes, warnings, or errors.

---

## API Design

### **Task API**
The task API provides endpoints for managing tasks. 

- **GET /tasks**: Fetches a list of all tasks.
- **POST /tasks**: Creates a new task.
- **GET /tasks/{task_id}**: Retrieves details of a specific task.
- **PUT /tasks/{task_id}**: Updates task details.
- **DELETE /tasks/{task_id}**: Deletes a task.

### **Performance API**
The performance API provides system metrics in JSON format.

- **GET /performance**: Fetches system metrics like CPU, memory, and disk usage.

### **Visualization API**
This API provides the data required for rendering visual graphs and charts.

- **GET /visualizations**: Retrieves the data required for rendering task completion rates and performance trends.

---

## WebSocket Implementation

WebSocket plays a central role in vAIn for real-time updates.

### WebSocket Flow
1. **Connection Establishment**: Clients connect to the WebSocket server at `ws://localhost/ws/tasks`.
2. **Events**:
   - `taskUpdate`: Sent when a task's status changes (e.g., from "pending" to "in-progress").
   - `performanceUpdate`: Sent when the performance metrics are updated.
   - `visualizationUpdate`: Updates related to trends and visualizations.
3. **Client Handling**: Clients listen for messages and update the UI in real time.

Example of WebSocket connection:

```javascript
const socket = new WebSocket("ws://localhost/ws/tasks");

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  if (data.type === "taskUpdate") {
    console.log(`Task ${data.task_id} updated to ${data.status}`);
  } else if (data.type === "performanceUpdate") {
    console.log(`Performance Update: CPU - ${data.cpu_usage}%`);
  }
};

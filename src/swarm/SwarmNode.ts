import { TaskRoutingSystem } from './TaskRoutingSystem';
import { StigmergyComm } from './StigmergyComm';

export class SwarmNode {
  private id: string;
  private specialization: string | null = null;
  private taskRouter: TaskRoutingSystem;
  private stigmergyComm: StigmergyComm;

  constructor(id: string) {
    this.id = id;
    this.taskRouter = new TaskRoutingSystem();
    this.stigmergyComm = new StigmergyComm();
  }

  public async processTask(task: Task): Promise<void> {
    const route = await this.taskRouter.findOptimalRoute(task);
    await this.stigmergyComm.leavePheromoneTrail(route);
    
    if (this.canHandleTask(task)) {
      await this.executeTask(task);
    } else {
      await this.delegateTask(task);
    }
  }

  private canHandleTask(task: Task): boolean {
    return this.specialization === null || 
           task.requiresSpecialization === this.specialization;
  }

  public specialize(role: string): void {
    this.specialization = role;
    this.stigmergyComm.broadcastSpecialization(this.id, role);
  }
}

export class TaskGroup {
  private members: Set<SwarmNode> = new Set();
  private taskType: string;
  private leader: SwarmNode | null = null;

  constructor(taskType: string) {
    this.taskType = taskType;
  }

  public async formGroup(initialProblem: Task): Promise<void> {
    const similarNodes = await this.findNodesWithSimilarTasks(initialProblem);
    this.leader = this.electLeader(similarNodes);
    await this.recruitMembers(similarNodes);
  }

  private async electLeader(nodes: SwarmNode[]): Promise<SwarmNode> {
    return nodes.reduce((best, current) => 
      current.getCapability() > best.getCapability() ? current : best
    );
  }

  public async distributeTask(task: Task): Promise<void> {
    const subTasks = this.leader!.decompose(task);
    await this.assignSubTasks(subTasks);
  }
}

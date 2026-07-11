package com.crosshub.amazon.service.impl;

import com.crosshub.agent.entity.AgentTask;
import com.crosshub.agent.service.impl.AgentServiceImpl;
import com.crosshub.amazon.service.AmazonWriteService;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class AmazonAgentWriteBridge implements AgentServiceImpl.AmazonWriteBridge {
    private final AmazonWriteService writeService;

    public AmazonAgentWriteBridge(AmazonWriteService writeService) {
        this.writeService = writeService;
    }

    @Override
    public void onAgentTaskStarted(AgentTask task) {
        if (task == null || !AmazonWriteService.WRITE_TASK_TYPE.equals(task.getTaskType())) {
            return;
        }
        writeService.onAgentTaskStarted(task.getId());
    }

    @Override
    public void onAgentTaskCompleted(
            AgentTask task,
            String status,
            Map<String, Object> result,
            String errorCode,
            String errorMessage
    ) {
        if (task == null || !AmazonWriteService.WRITE_TASK_TYPE.equals(task.getTaskType())) {
            return;
        }
        writeService.onAgentTaskCompleted(task.getId(), status, result, errorCode, errorMessage);
    }
}

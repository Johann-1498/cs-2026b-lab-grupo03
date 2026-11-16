import { type Message, SimulatedUser } from '../../providers/simulatedUser';
import type { ProviderResponse, TokenUsage } from '../../types';
type Config = {
    injectVar: string;
    maxTurns?: number;
    stateful?: boolean;
};
export default class RedteamMischievousUserProvider extends SimulatedUser {
    readonly taskId: string;
    constructor(config: Config);
    id(): string;
    serializeOutput(messages: Message[], tokenUsage: TokenUsage, finalTargetResponse: ProviderResponse): {
        output: string;
        tokenUsage: {
            prompt?: number | undefined;
            completion?: number | undefined;
            cached?: number | undefined;
            total?: number | undefined;
            numRequests?: number | undefined;
            completionDetails?: {
                reasoning?: number | undefined;
                acceptedPrediction?: number | undefined;
                rejectedPrediction?: number | undefined;
            } | undefined;
            assertions?: {
                prompt?: number | undefined;
                completion?: number | undefined;
                cached?: number | undefined;
                total?: number | undefined;
                numRequests?: number | undefined;
                completionDetails?: {
                    reasoning?: number | undefined;
                    acceptedPrediction?: number | undefined;
                    rejectedPrediction?: number | undefined;
                } | undefined;
            } | undefined;
        };
        metadata: {
            redteamFinalPrompt: string;
            messages: Message[];
            redteamHistory: {
                prompt: string;
                output: string;
            }[];
        };
        guardrails: import("../../types").GuardrailResponse | undefined;
    };
}
export {};
//# sourceMappingURL=mischievousUser.d.ts.map
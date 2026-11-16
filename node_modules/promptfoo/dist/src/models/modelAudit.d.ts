import type { ModelAuditScanResults } from '../types/modelAudit';
export declare function createScanId(createdAt?: Date): string;
export interface ModelAuditRecord {
    id: string;
    createdAt: number;
    updatedAt: number;
    name?: string | null;
    author?: string | null;
    modelPath: string;
    modelType?: string | null;
    results: ModelAuditScanResults;
    checks?: ModelAuditScanResults['checks'] | null;
    issues?: ModelAuditScanResults['issues'] | null;
    hasErrors: boolean;
    totalChecks?: number | null;
    passedChecks?: number | null;
    failedChecks?: number | null;
    metadata?: Record<string, any> | null;
}
export default class ModelAudit {
    id: string;
    createdAt: number;
    updatedAt: number;
    name?: string | null;
    author?: string | null;
    modelPath: string;
    modelType?: string | null;
    results: ModelAuditScanResults;
    checks?: ModelAuditScanResults['checks'] | null;
    issues?: ModelAuditScanResults['issues'] | null;
    hasErrors: boolean;
    totalChecks?: number | null;
    passedChecks?: number | null;
    failedChecks?: number | null;
    metadata?: Record<string, any> | null;
    persisted: boolean;
    constructor(data: Partial<ModelAuditRecord> & {
        persisted?: boolean;
    });
    static create(params: {
        name?: string;
        author?: string;
        modelPath: string;
        modelType?: string;
        results: ModelAuditScanResults;
        metadata?: Record<string, any>;
    }): Promise<ModelAudit>;
    static findById(id: string): Promise<ModelAudit | null>;
    static findByModelPath(modelPath: string): Promise<ModelAudit[]>;
    static getMany(limit?: number): Promise<ModelAudit[]>;
    static getLatest(limit?: number): Promise<ModelAudit[]>;
    /**
     * Get the most recent model audit scan.
     * @returns The latest model audit or undefined if none exists.
     */
    static latest(): Promise<ModelAudit | undefined>;
    save(): Promise<void>;
    delete(): Promise<void>;
    toJSON(): ModelAuditRecord;
}
//# sourceMappingURL=modelAudit.d.ts.map
import { z } from 'zod';

const errorSchema = z.object({
	success: z.literal(false),
	error: z.string()
});

const tokenFlowSuccessSchema = z.object({
	success: z.literal(true),
	web_url: z.string(),
	code: z.string()
});

export const tokenFlowSchema = z.union([tokenFlowSuccessSchema, errorSchema]);

const tokenFlowWaitSuccessSchema = z.object({
	success: z.literal(true)
});

export const tokenFlowWaitSchema = z.union([tokenFlowWaitSuccessSchema, errorSchema]);

const deploySuccessSchema = z.object({
	success: z.literal(true),
	modal_url: z.string()
});

export const deploySchema = z.union([deploySuccessSchema, errorSchema]);

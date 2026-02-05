SCHEMA_INSTRUCTIONS = """
You must return a JSON object that follows this schema (TypeScript/Zod).
Important parsing guidance:
- The brochure text may contain flattened tables where ranks, categories, and amounts appear on the same line or columnar layout is lost.
- Infer prize mappings by proximity and ordering. Example: "1st 2500 2nd 2000 3rd 1500 Trophy" means 1st=2500, 2nd=2000, 3rd=1500, and Trophy is a non-cash award.
- If a line contains category words (e.g., Best, Female, Veteran, Youngest, Oldest, U-15, U-19), map the nearest amount or non-cash award to that category.
- If amounts are missing but awards like Trophy/Certificate appear, capture them in prizeFund.nonCashAwards and/or specialPrizes with amount null.
- Prefer extracting a best-effort value rather than leaving fields null when a nearby amount or award likely belongs to the label.
- For schedule lines like "1st 09:15 am 2nd 10:15 am ... 9th 05:45 pm", treat each round number as a separate round and map its time to roundsSchedule.startTime.
- If special prize labels (e.g., Youngest, Oldest, Best Academy) appear near a list of amounts, pair them in order. If amounts appear on the same line, still map by proximity.

export const BrochureAnalysisSchema = z.object({
    tournamentName: z.string(),
    organizer: z.string(),
    organizingCommittee: z.array(z.object({
        name: z.string(),
        role: z.string().nullable(),
    })).nullable(),
    venue: z.object({
        location: z.string(),
        city: z.string(),
        state: z.string(),
    }),
    dates: z.object({
        registrationStart: z.string().nullable(),
        registrationEnd: z.string().nullable(),
        tournamentStart: z.string(),
        tournamentEnd: z.string(),
    }),
    schedule: z.object({
        rounds: z.number().nullable(),
        roundsSchedule: z.array(z.object({
            roundNumber: z.number(),
            date: z.string().nullable(),
            startTime: z.string().nullable(),
            endTime: z.string().nullable(),
            time: z.string().nullable(),
        })).nullable(),
        activities: z.array(z.object({
            name: z.string(),
            startTime: z.string().nullable(),
            endTime: z.string().nullable(),
        })).nullable(),
    }),
    format: z.string(),
    timeControl: z.string(),
    tieBreakers: z.array(z.string()).nullable(),
    eventCodes: z.array(z.string()).nullable(),
    categories: z.array(z.object({
        name: z.string(),
        description: z.string().nullable(),
        isSpecial: z.boolean().nullable(),
    })),
    prizeFund: z.object({
        total: z.string(),
        currency: z.string(),
        prizesByCategory: z.array(z.object({
            category: z.string(),
            prizes: z.array(z.object({
                position: z.string(),
                amount: z.string(),
            })),
        })),
        specialPrizes: z.array(z.object({
            title: z.string(),
            amount: z.string(),
            criteria: z.string().nullable(),
        })).nullable(),
        nonCashAwards: z.array(z.string()).nullable(),
    }),
    entryFees: z.array(z.object({
        category: z.string(),
        amount: z.string(),
        lastDate: z.string().nullable(),
    })),
    offers: z.array(z.object({
        description: z.string(),
        details: z.string(),
    })).nullable(),
    registration: z.object({
        howToRegister: z.string().nullable(),
        whereToRegister: z.string().nullable(),
        registrationLink: z.string().nullable(),
        feeAmount: z.string().nullable(),
        paymentDetails: z.object({
            accountHolderName: z.string().nullable(),
            bankName: z.string().nullable(),
            branch: z.string().nullable(),
            ifsc: z.string().nullable(),
            accountNumber: z.string().nullable(),
        }).nullable(),
    }),
    rules: z.array(z.string()).nullable(),
    eligibility: z.string().nullable(),
    rating: z.object({
        required: z.boolean(),
        type: z.string().nullable(),
        minRating: z.number().nullable(),
    }).nullable(),
    benefits: z.array(z.string()).nullable(),
    arbiters: z.array(z.object({
        name: z.string(),
        title: z.string().nullable(),
        role: z.string().nullable(),
    })).nullable(),
    contacts: z.array(z.object({
        name: z.string().nullable(),
        role: z.string().nullable(),
        phone: z.string().nullable(),
        email: z.string().nullable(),
        isImportant: z.boolean().nullable(),
    })),
    sponsors: z.array(z.object({
        name: z.string(),
        type: z.string().nullable(),
    })).nullable(),
    recognisedBy: z.array(z.string()).nullable(),
    otherData: z.array(z.string()).nullable(),
    importantNotes: z.array(z.string()).nullable(),
    summary: z.string(),
});
"""

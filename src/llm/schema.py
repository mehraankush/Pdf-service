SCHEMA_INSTRUCTIONS = """
You must return a JSON object that follows this schema (TypeScript/Zod):

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
        name: z.string(),
        role: z.string().nullable(),
        phone: z.string(),
        email: z.string().nullable(),
        isImportant: z.boolean().nullable(),
    })),
    sponsors: z.array(z.object({
        name: z.string(),
        type: z.string().nullable(),
    })).nullable(),
    importantNotes: z.array(z.string()).nullable(),
    summary: z.string(),
});
"""

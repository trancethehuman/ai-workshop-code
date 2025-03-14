LINKEDIN_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "current_role": {
            "type": "string",
            "description": "The current job title of the person on LinkedIn.",
        },
        "company": {
            "type": "string",
            "description": "The name of the company where the person is currently employed.",
        },
        "industry": {
            "type": "string",
            "description": "The industry the person works in.",
        },
        "experience": {
            "type": "array",
            "description": "A list of previous job positions held by the person.",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The job title of the position held.",
                    },
                    "company": {
                        "type": "string",
                        "description": "The name of the company where the job was held.",
                    },
                    "duration": {
                        "type": "string",
                        "description": "The duration of time spent in the position.",
                    },
                },
                "required": ["title", "company", "duration"],
                "additionalProperties": False,
            },
        },
        "education": {
            "type": "array",
            "description": "A list of educational qualifications.",
            "items": {
                "type": "string",
                "description": "Educational qualification in format: Degree, Institution, Year",
            },
        },
        "interests": {
            "type": "array",
            "description": "A list of professional interests mentioned on the profile.",
            "items": {
                "type": "string",
                "description": "A professional interest or topic",
            },
        },
        "recent_activity": {
            "type": "string",
            "description": "Brief description of recent activity on LinkedIn, if visible.",
        },
    },
    "required": [
        "current_role",
        "company",
        "industry",
        "experience",
        "education",
        "interests",
        "recent_activity",
    ],
    "additionalProperties": False,
}

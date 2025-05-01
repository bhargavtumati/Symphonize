import { filter } from "lodash";

export default function getApplicantPreferredData(applicantsPreferences: any, jobData: any) {
    if (applicantsPreferences) {
        return applicantsPreferences;
    }
    else {
        const defaultData = {
            filters: {
                industry_type: jobData?.job?.enhanced_description?.industry_type,
                remuneration: {
                    name: "Salary Range",
                    min: jobData?.job?.enhanced_description?.salary?.min_value || 1,
                    max: jobData?.job?.enhanced_description?.salary?.max_value || 2,
                },
                skills: jobData?.job?.enhanced_description?.skills,
                responsibilities: jobData?.job?.enhanced_description?.responsibilities,
                availability: jobData?.job?.enhanced_description?.availability !== "Not provided"
                    ? {
                        name: "Can Join in",
                        value: jobData?.job?.enhanced_description?.availability || 0,
                    }
                    : {
                        name: "",
                        value: 0,
                    },
                workmode: jobData?.job?.enhanced_description?.workmode,
                location: jobData?.job?.enhanced_description?.location,
                soft_skills: jobData?.job?.enhanced_description?.softskills,
                transition_behaviour: jobData?.job?.enhanced_description?.transition_behaviour !== "Not provided"
                    ? [
                        {
                            name: "Avg. Duration in Previous Companies",
                            preference: "Good to have",
                            value: jobData?.job?.enhanced_description?.transition_behaviour || 0,
                        },
                    ]
                    : [
                        {
                            name: "",
                            preference: "",
                            value: 0,
                        },
                    ],
            },
        };
        return defaultData;
    }

   // return applicantsPreferences ? applicantsPreferences : defaultData;
}
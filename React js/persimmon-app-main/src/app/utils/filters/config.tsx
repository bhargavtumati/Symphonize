export const filterconfig = {
    industry:{
        industryExperienceRange: 50,
        addIndustry:{
            name: "Software Development",
            pref: "Good to have",
            max: 5,
            min: 4,
            isEditing: true,
            errorMessage: "",
            checked: false,
        }
    },
    remunration:{
        remunerationRange: 100,
    },
    skills:{
        skillRange: 10,
        addSkill: {
            name: "",
            isEditing: true,
            errorMessage: "",
            rating: 4,
            experience: 2,
            pref: "Good to have",
            checked: false,
        }
    },
    availability:{
        availabilityRange: 5,
        availabilityBreakPoints: [0, 15, 30, 60, 90, 99],
    },
    
    transitionBehavior: {
        transitionRange: 6,
        transitionBreakPoints: [0, 1, 2, 3, 4, 5,50],
        transitionName: "Avg. Duration in Previous Companies",
        transitionPreference:"Good to have",
    },
    softSkills:{
        addSoftSkill:{
            name: "",
            min_value: "5",
            max_value: "7",
            slider_value: 1,
            checked: false,
            errorMessage: "",
            pref: "Good to have",
            isEditing: true,
        }
    },
    otherFilter:{
        teamSize:{ value: "1-5", preference: "Good to have" },
        companySize:{ value: "1-10", preference: "Good to have" }
    }
};

export const preferenceOptions = [
    { value: "Good to have", label: "Good to have" },
    { value: "Preferred to have", label: "Preferred to have" },
    { value: "Must have", label: "Must have" },
  ]
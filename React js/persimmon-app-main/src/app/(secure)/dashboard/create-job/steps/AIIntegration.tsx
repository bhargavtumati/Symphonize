"use client"

import { Card } from "@/components/ui/card"
import type React from "react"
import { useState, useEffect } from "react"
import { Textarea } from "@/components/ui/textarea"
import Image from "next/image"
import { Info, Loader2 } from "lucide-react"
import TooltipComponent from "@/app/components/tooltip-component"
import { apiService } from "@/app/api/service"
import { cn } from "@/lib/utils"

interface AIDetails {
  aiInput: { [key: string]: string },
  enhanced_description: {}
}

interface StepProps {
  data: AIDetails
  questions: string[]
  onChange: (newData: AIDetails) => void
  errors: Partial<AIDetails>
  onBack: () => void
  onNext: () => void
  jobDescription: string
  originalJD: string
}

const Step4AIIntegration: React.FC<StepProps> = ({
  data,
  questions,
  onChange,
  errors,
  onBack,
  onNext,
  jobDescription,
  originalJD,
}) => {
  const [questionsData, setQuestions] = useState<string[]>(questions)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (originalJD !== jobDescription) {
      const fetchQuestions = async () => {
        if (jobDescription) {
          setLoading(true)
          try {
            const response = await apiService(`/jobs/generate-ai-clarifying-questions`, "POST", {
              description: jobDescription,
            })
            if (response.status === 200 && response.enhanced_description.clarifying_questions) {
              const newQuestions = response.enhanced_description.clarifying_questions
              setQuestions(newQuestions)
              console.log('enhanced jd', response.enhanced_description)
              // Initialize aiInput with all questions, even if they don't have answers
              const initializedAiInput = newQuestions.reduce((acc: { [key: string]: string }, question: string) => {
                acc[question] = data.aiInput[question] || ""
                return acc
              }, {})

              // Trigger onChange with all questions
              onChange({ aiInput: initializedAiInput, enhanced_description: response.enhanced_description })
            }
          } catch (error) {
            console.error("Error fetching AI clarifying questions:", error)
          } finally {
            setLoading(false)
          }
        }
      }

      fetchQuestions()
    } else {
      // If job description hasn't changed, still initialize aiInput with all questions
      const initializedAiInput = questionsData.reduce((acc: { [key: string]: string }, question: string) => {
        acc[question] = data.aiInput[question] || ""
        return acc
      }, {})

      // Trigger onChange with all questions
      onChange({ aiInput: initializedAiInput, enhanced_description: data.enhanced_description })
    }
  }, []) // Added data.aiInput to dependencies

  const handleInputChange = (questionIndex: number, answer: string) => {
    const updatedAiInput = {
      ...data.aiInput,
      [questionsData[questionIndex]]: answer,
    }
    onChange({ aiInput: updatedAiInput, enhanced_description: data.enhanced_description })
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questionsData.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
    }
  }

  return (
    <div className="flex flex-col md:flex-row gap-4">
      <Card className="w-full md:w-[70%] border-none p-8">
        <div className="p-6">
          <div className="flex items-center space-x-2 ">
            <h3 className="text-xl font-semibold mb-2">AI Clarifying Questions</h3>
            <TooltipComponent
              icon={<Info className="w-[18px] h-4 mb-2 text-yellow-500" />}
              message="These questions are solely for accurate matching algorithms, not for posting"
              tag="p"
              className="w-[220px] absolute top-full mt-6 -left-5 text-gray-700 font-medium rounded-lg"
            />
          </div>
          <p className="text-sm text-gray-600 mb-6">
            Provide additional information to the AI model to understand the requirement better.
          </p>

          <div className="grid grid-cols-1 gap-6">
            {loading ? (
              <div className="flex justify-center">
                <Loader2 className="animate-spin flex items-center justify-center" />
              </div>
            ) : questionsData.length > 0 ? (
              <div>
                <label className="block text-l font-medium text-gray-700">{questionsData[currentQuestionIndex]}</label>
                <Textarea
                  name="aiInput"
                  placeholder="Answer here"
                  value={data.aiInput[questionsData[currentQuestionIndex]] || ""}
                  onChange={(e) => handleInputChange(currentQuestionIndex, e.target.value)}
                  className="mt-2 block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm sm:text-l"
                />
                <div className="flex justify-between pt-4">
                  <button
                    className={cn(
                      "font-medium text-l flex items-center cursor-pointer",
                      currentQuestionIndex === 0 && "text-gray-400 cursor-not-allowed",
                    )}
                    onClick={handlePreviousQuestion}
                    disabled={currentQuestionIndex === 0}
                  >
                    <Image
                      src="/images/left.png"
                      alt=""
                      width={20}
                      height={20}
                      className={cn(currentQuestionIndex === 0 && "opacity-50")}
                    />
                    <span>Previous</span>
                  </button>
                  <button
                    className={cn(
                      "font-medium text-l flex items-center cursor-pointer",
                      currentQuestionIndex === questionsData.length - 1 && "text-gray-400 cursor-not-allowed",
                    )}
                    onClick={handleNextQuestion}
                    disabled={currentQuestionIndex === questionsData.length - 1}
                  >
                    <span>Next Question</span>
                    <Image
                      src="/images/right.png"
                      width={20}
                      height={20}
                      alt=""
                      className={cn(currentQuestionIndex === questionsData.length - 1 && "opacity-50")}
                    />
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex justify-center">No questions available</div>
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-4 mt-20 pr-6">
          <button
            type="button"
            onClick={onBack}
            className="bg-white border border-[1px] border-gray-300 px-4 py-2 rounded-md w-[105px] h-[40px]"
          >
            Back
          </button>
          <button
            type="button"
            onClick={onNext}
            className="bg-blue-600 text-white px-4 py-2 rounded-md  w-[105px] h-[40px]"
          >
            Next
          </button>
        </div>
      </Card>
    </div>
  )
}

export default Step4AIIntegration


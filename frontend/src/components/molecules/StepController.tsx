import { Button, ButtonGroup } from "@chakra-ui/react";

const StepController = ({
  step,
  setStep,
  isPrevDisabled,
  isNextDisabled,
}: {
  step: number;
  setStep: (step: number) => void;
  isPrevDisabled?: boolean;
  isNextDisabled?: boolean;
}) => {
  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  return (
    <ButtonGroup py={4}>
      <Button disabled={isPrevDisabled} onClick={prevStep}>
        Previous
      </Button>
      <Button disabled={isNextDisabled} onClick={nextStep}>
        Next
      </Button>
    </ButtonGroup>
  );
};

export default StepController;

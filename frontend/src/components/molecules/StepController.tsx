import { Button, ButtonGroup } from "@chakra-ui/react";
import { useContext } from "react";
import IndicatorFormContext from "../../utils/context/IndicatorFormContext";

const StepController = ({
  isPrevDisabled,
  isNextDisabled,
}: {
  isPrevDisabled?: boolean;
  isNextDisabled?: boolean;
}) => {
  const { step, setStep } = useContext(IndicatorFormContext);

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

import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { UseCases } from "./components/UseCases";
import { WhyHongKong } from "./components/WhyHongKong";

export default function LandingPage() {
  return (
    <>
      <Hero />
      <WhyHongKong />
      <UseCases />
      <HowItWorks />
    </>
  );
}

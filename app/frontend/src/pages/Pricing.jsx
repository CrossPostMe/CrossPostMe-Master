import React from "react";
import { pricingPlans } from '../mock/data';

const Pricing = () => {
  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-8">Pricing</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pricingPlans.map((plan, index) => (
            <div key={index} className={`bg-gray-50 rounded-lg shadow p-8 flex flex-col items-center ${plan.popular ? 'border-2 border-blue-500' : ''}`}>
              <h3 className="text-2xl font-semibold mb-2">{plan.name}</h3>
              <p className="text-3xl font-bold mb-4">{typeof plan.price === 'number' ? `$${plan.price}/mo` : plan.price}</p>
              <ul className="mb-4 text-gray-600 list-disc list-inside">
                {plan.features.map((feature, i) => (
                  <li key={i}>{feature}</li>
                ))}
              </ul>
              <button className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">
                {typeof plan.price === 'number' ? 'Get Started' : 'Request Pricing'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;

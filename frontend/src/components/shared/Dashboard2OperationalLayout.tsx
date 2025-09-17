import React from 'react';
import { motion } from 'framer-motion';

interface Dashboard2OperationalLayoutProps {
  // 1ère rangée (50/50)
  teamAvailability: React.ReactNode;
  weeklyPlanning: React.ReactNode;
  
  // 2ème rangée (100%)
  cashFlow: React.ReactNode;
  
  // 3ème rangée (65/35)
  actionPlan: React.ReactNode;
  lastVideo: React.ReactNode;
}

const Dashboard2OperationalLayout: React.FC<Dashboard2OperationalLayoutProps> = ({
  teamAvailability,
  weeklyPlanning,
  cashFlow,
  actionPlan,
  lastVideo
}) => {
  return (
    <motion.div 
      className="h-full flex flex-col gap-4 p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* 1ère rangée : TeamAvailability (50%) + WeeklyPlanning (50%) */}
      <div className="flex gap-4 flex-1">
        <motion.div 
          className="flex-1"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          {teamAvailability}
        </motion.div>
        
        <motion.div 
          className="flex-1"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          {weeklyPlanning}
        </motion.div>
      </div>

      {/* 2ème rangée : Cash Flow (100% largeur) */}
      <motion.div 
        className="flex-1"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {cashFlow}
      </motion.div>

      {/* 3ème rangée : ActionPlan (65%) + LastVideo (35%) */}
      <div className="flex gap-4 flex-1">
        <motion.div 
          className="flex-[65]"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          {actionPlan}
        </motion.div>
        
        <motion.div 
          className="flex-[35]"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          {lastVideo}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Dashboard2OperationalLayout;
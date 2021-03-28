import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import matplotlib.animation as ani
from matplotlib.widgets import Button
import functools

sns.set()

class BanditEnv():

	def __init__(self,num_arms,means=None,standard_deviations=None):
		
		self.num_arms=num_arms
		
		if means is None:
			self.num_arms=num_arms
			self.means=list(10*np.random.random((num_arms-1)))
			self.means.insert(0,10)
			self.standard_deviations=list(np.random.random((num_arms-1))+1.2)
			self.standard_deviations.insert(0,1.2)
		elif means=='rand':
			self.means=list(10*np.random.random((num_arms)))
			self.standard_deviations=list(np.random.random((num_arms))+1.2)
		else:
			assert len(means)==len(standard_deviations)
			self.num_arms=len(means)
			self.means=means
			self.standard_deviations=standard_deviations
		
		return
		
	def pull_arm(self,arm):
		
		mu=self.means[arm]
		sigma=self.standard_deviations[arm]
		
		return np.random.normal(mu,sigma**2)
	
	def make_background(self,show_dists=1,show_regret=1):
		self.COLOURS=sns.color_palette("Set2",self.num_arms)
		self.COLOURS2=sns.color_palette("Paired")

		if show_regret:
			fig,axs=plt.subplots(2,1, gridspec_kw={'height_ratios': [3, 1],'width_ratios': [1] })
			fig.canvas.set_window_title('UCB Demo') 
			ax=axs[0]
			ax2=axs[1]
		else:
			fig,ax=plt.subplots(1,1)
			fig.canvas.set_window_title('UCB Demo') 
			ax2=None

		if show_dists:
			for arm in range(self.num_arms):
				mu=self.means[arm]
				sigma=self.standard_deviations[arm]
				rect = patches.Rectangle((0,-10),1,25,facecolor='w',zorder=0)
				ax.add_patch(rect)
				sns.kdeplot(np.random.normal(mu,sigma**2,(100000)), color=self.COLOURS[arm],shade=False,vertical=True,alpha=1.0,ax=ax,kernel='gau')
				separation=1.0/self.num_arms
				ax.plot([-separation*(self.num_arms+0.5),0],[mu,mu],':',lw=3,c=self.COLOURS[arm])
				ax.set_xlim([-separation*(self.num_arms+0.5),0.35])
		else:
			separation=1.0/self.num_arms
			ax.set_xlim([-separation*(self.num_arms+0.5),0])
			
		return fig,ax,ax2


class UCB():
	
	def __init__(self,bandit_env,delta):
		
		self.bandit_env=bandit_env
		self.num_arms=self.bandit_env.num_arms
		self.delta=delta
					
		self.times_pulled=None
		self.rewards=None
		self.upper_confidence_bounds=None
		
		self.figure=None
		
   
	
	def initialize(self,samples=None):
		
		self.times_pulled=[1 for arm in range(self.num_arms)]
		self.rewards=[[] for arm in range(self.num_arms)]
		self.upper_confidence_bounds=[0 for arm in range(self.num_arms)]
		
		if samples is None:
			for arm in range(self.num_arms): 
				reward=self.bandit_env.pull_arm(arm)
				self.rewards[arm].append(reward)
				self.upper_confidence_bounds[arm]=reward+np.sqrt(2*np.log(1/self.delta)/self.times_pulled[arm])
		
		return 
	
	def choose_arm_and_update_bounds(self, event,show_dists=1,show_regret=1):
		
		arm=np.argmax(self.upper_confidence_bounds)
		reward=self.bandit_env.pull_arm(arm)
		self.times_pulled[arm]+=1
		self.rewards[arm].append(reward)
		self.pseudo_regret+=np.max(self.bandit_env.means)-self.bandit_env.means[arm]
		self.regret.append(self.pseudo_regret)
		
		sample_mean=np.mean(self.rewards[arm])
		self.upper_confidence_bounds[arm]=sample_mean+np.sqrt(2*2.2**2*np.log(2/self.delta)/self.times_pulled[arm])

		self.viewBounds(show_dists,show_regret)
		if show_regret:
			self.ax2.plot(self.regret,'-.',c=self.bandit_env.COLOURS2[1])
			self.ax2.set_xlabel('Time (t)',fontsize=10)
			self.ax2.set_ylabel('Pseudo-regret',fontsize=10)
		plt.draw()
		return arm,reward
		

	def interactive_choose_arm_and_update_bounds(self,event,pull=-1,show_dists=1,show_regret=1):

		arm=pull
		reward=self.bandit_env.pull_arm(arm)
		self.times_pulled[arm]+=1
		self.rewards[arm].append(reward)
		self.pseudo_regret+=np.max(self.bandit_env.means)-self.bandit_env.means[arm]
		self.regret.append(self.pseudo_regret)
		
		sample_mean=np.mean(self.rewards[arm])
		self.upper_confidence_bounds[arm]=sample_mean+np.sqrt(2*2.2**2*np.log(2/self.delta)/self.times_pulled[arm])

		self.viewBounds(show_dists,show_regret)
		if show_regret:
			self.ax2.plot(self.regret,'-.',c=self.bandit_env.COLOURS2[1])
			self.ax2.set_xlabel('Time (t)',fontsize=10)
			self.ax2.set_ylabel('Pseudo-regret',fontsize=10)
		plt.draw()

		return arm,reward



	def run_Interactive(self,dists=1,reg=1,show_UCB=1):
		
		self.initialize()
		self.pseudo_regret=0
		self.regret=[]
		self.viewBounds(dists,reg)
		self.regret.append(self.pseudo_regret)
		if reg:
			self.ax2.plot(self.regret,'-.',c=self.bandit_env.COLOURS2[1])
			self.ax2.set_xlabel('Time (t)',fontsize=10)
			self.ax2.set_ylabel('Pseudo-regret',fontsize=10)

		self._make_buttons(dists,reg,show_UCB)

		plt.show()

		return self.regret

	def _make_buttons(self,dists=1,reg=1,show_UCB=1):

		self.buttons=[]
		textstarts=[]
		separation=1.0/self.num_arms
		axes_height=2.5
		axes_width=0.5*separation
		width,h=self.figure.transFigure.inverted().transform(self.ax.transData.transform([axes_width,0]))-self.figure.transFigure.inverted().transform(self.ax.transData.transform([0,0]))

		w,height=self.figure.transFigure.inverted().transform(self.ax.transData.transform([0,axes_height]))-self.figure.transFigure.inverted().transform(self.ax.transData.transform([0,0]))

		for arm in range(self.num_arms):
			location=-separation*(self.num_arms-arm)
			t1,t2=self.figure.transFigure.inverted().transform(self.ax.transData.transform([location-axes_width/2.0,-8.5]))
			textstarts.append([t1,t2,width,height])


		for arm in range(self.num_arms):
			self.buttons.append(Button(plt.axes(textstarts[arm]),str(arm),color=self.bandit_env.COLOURS[arm], hovercolor=self.bandit_env.COLOURS2[1]))

			self.buttons[-1].on_clicked(functools.partial(self.interactive_choose_arm_and_update_bounds, pull=arm,show_dists=dists,show_regret=reg))

		if show_UCB:
			if dists:

				t1,t2=self.figure.transFigure.inverted().transform(self.ax.transData.transform([0.1,-8.5]))
				textstarts.append([t1,t2,width,height])

				self.buttons.append(Button(plt.axes([t1, t2, 2*width, height]),'UCB',color=self.bandit_env.COLOURS2[0], hovercolor=self.bandit_env.COLOURS2[1]))

				self.buttons[-1].on_clicked(functools.partial(self.choose_arm_and_update_bounds, show_dists=dists,show_regret=reg))

			else:
				t1,t2=self.figure.transFigure.inverted().transform(self.ax.transData.transform([-0.5-2*axes_width,-12.5]))
				textstarts.append([t1,t2,width,height])

				self.buttons.append(Button(plt.axes([t1, t2, 2*width, height]),'UCB',color=self.bandit_env.COLOURS2[0], hovercolor=self.bandit_env.COLOURS2[1]))

				self.buttons[-1].on_clicked(functools.partial(self.choose_arm_and_update_bounds, show_dists=dists,show_regret=reg))




	def viewBounds(self,show_dists=1,show_regret=1):
		if self.figure is None:
			self.figure,self.ax,self.ax2=self.bandit_env.make_background(show_dists,show_regret)
		else:
			for line in self.plot_content:
				line.remove()

		self.plot_content=[]
		
		for arm in range(self.num_arms):
			separation=1.0/self.num_arms
			location=-separation*(self.num_arms-arm)
			self.plot_content.extend(self.ax.plot([location,location],[np.mean(self.rewards[arm]),self.upper_confidence_bounds[arm]],lw=2.5,c=self.bandit_env.COLOURS[arm]))
			self.plot_content.extend(self.ax.plot([-separation*(self.num_arms-arm-0.25),-separation*(self.num_arms-arm+0.25)],[self.upper_confidence_bounds[arm],self.upper_confidence_bounds[arm]],'-',lw=3,c=self.bandit_env.COLOURS[arm]))
			self.plot_content.extend(self.ax.plot([location],[np.mean(self.rewards[arm])],'.',ms=15,c=self.bandit_env.COLOURS[arm]))
			
			if self.num_arms<=8:
				self.plot_content.append(self.ax.text(location, -3, r' Arm {}'.format(arm),ha='center',va='center',fontsize= min(60/(self.num_arms),10)))
				self.plot_content.append(self.ax.text(location, -4.6, r'$n_{}={}$'.format(arm,self.times_pulled[arm]),ha='center', va='center',fontsize= min(60/(self.num_arms),10,)))
		
		if show_dists:
			self.ax.set_ylim([-10,15])
		else:
			self.ax.set_ylim([-13,15])
		self.ax.set_xticks([])
		self.ax.set_ylabel('Rewards',fontsize=15)
		self.figure.canvas.set_window_title('UCB Demo') 
		return


if __name__ == "__main__":
	
	num_arms=6
	T=200
	num_runs=1
	show=1
	env=BanditEnv(num_arms, 'rand')

	alg1=UCB(env,1.0/(T)**2)
	ucb_regret=0
	for run in range(num_runs):
		print('UCB Run: '+str(run))
		ucb_regret+=np.array(alg1.run_Interactive(1,0,0))

	plt.plot(ucb_regret)
	plt.xlabel('Time (t)',fontsize=10)
	plt.ylabel('Pseudo-regret',fontsize=10)
	plt.show()






 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
# Copyright (C) IBM Corporation 2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""cog.py: Implementation of Google's COG dataset. https://arxiv.org/abs/1803.06092"""

__author__ = "Emre Sevgen"

import torch
import gzip
import json
import os
import numpy as np

from miprometheus.problems.seq_to_seq.VQA.VQA_problem import VQAProblem
from miprometheus.problems.seq_to_seq.VQA.cog.cog_utils import json_to_img as jti

class COGDataset(VQAProblem):
	"""
	The COG dataset is a sequential VQA dataset. Inputs are a sequence of images of simple shapes and characters on a black \
 	background, and a question based on these objects that relies on memory which has to be answered at every step of the \
	sequence.

	"""

	def __init__(self, params):
		"""
		Initializes the COG Dataset problem:

			- Calls ``problems.problem.VideoTextToClassProblem`` class constructor,
			- Sets the following attributes using the provided ``params``:

				- ``self.root_folder`` (`string`) : Root directory of dataset where ``processed/training.pt``\
					and ``processed/test.pt`` will be saved,
				- ``self.data_folder`` (`string`) : Data directory where dataset is stored. If using canonical \
									or hard dataset, simply point to 'data_X_Y_Z' folder.
				- ``self.set`` (`string`) : 'val', 'test', or 'train'
				- ``self.tasks`` (`string or list of string`) : Which tasks to use. 'class', 'reg', 'all', or a 
\ list of tasks such as ['AndCompareColor', 'AndCompareShape']. Only selected tasks will be used.
				- ``self.dataset_type`` (`string`) : Which dataset to use, 'canonical', 'hard', or \
								'generated'. If 'generated', please specify 'sequence_length', \
								'memory_length', and 'max_distractors'.

		:param params: Dictionary of parameters (read from configuration ``.yaml`` file).

		"""
	
		# Call base class constructors
		super(COGDataset, self).__init__(params)

		# Set default parameters.
		self.params.add_default_params({'root_folder': os.path.expanduser('~/data/COG'), 
																		'data_folder': os.path.expanduser('~/data/COG'), 
																		'set': 'train', 
																		'tasks': 'class', 
																		'dataset_type': 'canonical'})

		# Retrieve parameters from the dictionary
		self.root_folder= os.path.expanduser(params['root_folder'])
		self.data_folder= os.path.expanduser(params['data_folder'])
		self.set	= params['set']
		assert self.set in ['val','test','train'], "set in configuration file must be one of 'val', 'test', or 'train', "\
								"got {}".format(self.set)
		self.dataset_type	= params['dataset_type']
		assert self.dataset_type in ['canonical','hard','generated'], "dataset in configuration file must be one of "\
								"'canonical', 'hard', or 'generated', got {}".format(self.dataset_type)

		# Parse task and dataset_type
		self.parse_tasks_and_dataset_type(params)
	
		# Name
		self.name = 'COGDataset'

		# This is set for now.
		self.img_size = 112

		# Set default values
		self.default_values = {	'height': self.img_size,
														'width': self.img_size,
														'num_channels': 3,
														'sequence_length' : self.sequence_length}
		
		# Set data dictionary based on parsed dataset type
		self.data_definitions = {'images': {'size': [-1, self.sequence_length, 3, 112, 112], 'type': [torch.Tensor]},
					'tasks':	{'size': [-1, 1], 'type': [list, str]},
					'questions': 	{'size': [-1, 1], 'type': [list, str]},
					'targets_reg' :	{'size': [-1, self.sequence_length, 2], 'type': [torch.Tensor]},
					'targets_class':{'size': [-1, self.sequence_length, 1], 'type' : [list,str]}
					}		

		assert os.path.isdir(self.data_folder_path), "Data directory not found at {}. Please download the dataset and "\
	"point to the correct directory.".format(self.data_folder_path)
		

		# Load all the .jsons, but image generation is done in __getitem__
		self.dataset = {}
		self.length = 0
	
		for tasklist in os.listdir(self.data_folder_path):
			if tasklist[4:-8] in self.tasks:
				self.dataset[(tasklist[4:-8])]=[]
				with gzip.open(os.path.join(self.data_folder_path,tasklist)) as f:
					fulltask = f.read().decode('utf-8').split('\n')
					for datapoint in fulltask:
						self.dataset[tasklist[4:-8]].append(json.loads(datapoint))
				self.length = self.length + len(self.dataset[tasklist[4:-8]])


	def __getitem__(self, index):
		"""
		Getter method to access the dataset and return a sample.

		:param index: index of the sample to return.
		:type index: int
		:return: ``DataDict({'images', 'questions', 'targets', 'targets_label'})``, with:
		
			-images:	Sequence of images,
			-tasks:		Which task family sample belongs to
			-questions:	Question on the sequence (this is constant per sequence for COG),
			-targets_reg:	Sequence of targets as tuple of floats for pointing tasks
			-targets_class:	Sequence of word targets for classification tasks

		"""
		# With the assumption that each family has the same number of examples
		i = index % len(self.tasks)
		j = int(index / len(self.tasks))

		# This returns:
		# All variables are numpy array of float32
			# in_imgs: (n_epoch*batch_size, img_size, img_size, 3)
			# in_rule: (max_seq_length, batch_size) the rule language input, type int32
			# seq_length: (batch_size,) the length of each task instruction
			# out_pnt: (n_epoch*batch_size, n_out_pnt)
			# out_pnt_xy: (n_epoch*batch_size, 2)
			# out_word: (n_epoch*batch_size, n_out_word)
			# mask_pnt: (n_epoch*batch_size)
			# mask_word: (n_epoch*batch_size)		
		output = jti.json_to_feeds([self.dataset[self.tasks[i]][j]])[0]
		images = ((torch.from_numpy(output)).permute(1,0,4,2,3)).squeeze()
				
		data_dict = self.create_data_dict()
		data_dict['images']	= images
		data_dict['tasks']	= [self.tasks[i]]
		data_dict['questions']	= [self.dataset[self.tasks[i]][j]['question']]
		answers = self.dataset[self.tasks[i]][j]['answers']
		if self.tasks[i] in self.classification_tasks:
			data_dict['targets_reg']	= torch.FloatTensor([0,0]).expand(self.sequence_length,2)
			data_dict['targets_class'] 	= answers
		else :
			data_dict['targets_reg']	= torch.FloatTensor([[-1,-1] if reg == 'invalid' else reg for reg in answers])
			data_dict['targets_class'] 	= [' ' for item in answers]



		return(data_dict)

	def collate_fn(self, batch):
		"""
		Combines a list of ``DataDict`` (retrieved with ``__getitem__``) into a batch.

		:param batch: list of individual ``DataDict`` samples to combine.
		:return: ``DataDict({'images', 'tasks', 'questions', 'targets_reg', 'targets_class'})`` containing the batch.
		"""
		#return DataDict({key: value for key, value in zip(self.data_definitions.keys(),
                #                                          super(COGDataset, self).collate_fn(batch).values())})

		data_dict = self.create_data_dict()
		
		data_dict['images'] = torch.stack([image['images'] for image in batch]).type(torch.FloatTensor)
		data_dict['tasks']  = [task['tasks'] for task in batch]
		data_dict['questions'] = [question['questions'] for question in batch]
		data_dict['targets_reg'] = torch.stack([reg['targets_reg'] for reg in batch]).type(torch.FloatTensor)
		data_dict['targets_class'] = [tgclassif['targets_class'] for tgclassif in batch]

		return data_dict


	def parse_tasks_and_dataset_type(self, params):
		"""
		Parses the task list and dataset type. Then sets folder paths to appropriate values.

		:param params: Dictionary of parameters (read from the configuration ``.yaml`` file).
		:type params: miprometheus.utils.ParamInterface
		"""

		self.classification_tasks = ['AndCompareColor','AndCompareShape','AndSimpleCompareColor','AndSimpleCompareShape','CompareColor','CompareShape','Exist',
'ExistColor','ExistColorOf','ExistColorSpace','ExistLastColorSameShape','ExistLastObjectSameObject','ExistLastShapeSameColor',
'ExistShape','ExistShapeOf','ExistShapeSpace','ExistSpace','GetColor','GetColorSpace','GetShape','GetShapeSpace','SimpleCompareColor',
'SimpleCompareShape'] 

		self.regression_tasks =['AndSimpleExistColorGo','AndSimpleExistGo','AndSimpleExistShapeGo','CompareColorGo','CompareShapeGo','ExistColorGo',
'ExistColorSpaceGo','ExistGo','ExistShapeGo','ExistShapeSpaceGo','ExistSpaceGo','Go','GoColor','GoColorOf','GoShape','GoShapeOf',
'SimpleCompareColorGo','SimpleCompareShapeGo','SimpleExistColorGo','SimpleExistGo','SimpleExistShapeGo'] 

		self.tasks = params['tasks']
		if self.tasks == 'class':
			self.tasks = self.classification_tasks
		elif self.tasks == 'reg':
			self.tasks = self.regression_tasks
		elif self.tasks == 'all':
			self.tasks = self.classification_tasks + self.regression_tasks

		# If loading a default dataset, set default path names and set sequence length
		folder_name_append = ' '
		
		if self.dataset_type == 'canonical':
			folder_name_append = '_4_3_1'			
			self.sequence_length = 4
		elif self.dataset_type == 'hard':
			folder_name_append = '_8_7_10'			
			self.sequence_length = 8
		elif self.dataset_type == 'generated':
			try:
				self.sequence_length = params['dataset_type']['sequence_length']
				self.memory_length = params['dataset_type']['memory_length']
				self.max_distractors = params['dataset_type']['max_distractors']
			except KeyError:
				print("Please specify sequence length, memory length and maximum distractors for a generated dataset under 'dataset_type'.")

		# Open using default folder path if using a pregenerated dataset
		if self.dataset_type != 'generated':
			self.data_folder_path = os.path.join(self.data_folder,'data'+folder_name_append,self.set+folder_name_append)
		else:
			self.data_folder_path = self.data_folder

	def add_statistics(self, stat_col):
		"""
		Add cog-specific stats to ``StatisticsCollector``.
		
		:param stat_col: ``StatisticsCollector``.
		
		"""
		stat_col.add_statistic('seq_len', '{:06d}')
		stat_col.add_statistic('max_mem', '{:06d}')
		stat_col.add_statistic('max_distractors', '{:06d}')
		stat_col.add_statistic('task', '{}')

	def collect_statistics(self, stat_col, data_dict, logits):
		"""
		Collects dataset details.
		:param stat_col: ``StatisticsCollector``.
		:param data_dict: DataDict containing targets.
		:param logits: Prediction of the model.

		"""
		stat_col['seq_len'] = self.sequence_length
		stat_col['max_mem'] = self.memory_length
		stat_col['max_distractors'] = self.max_distractors
		stat_col['task'] = data_dict['tasks']		
		

if __name__ == "__main__":
	
	""" 
	Unit test that checks data dimensions match expected values, and generates an image.
	Checks one regression and one classification task.
	"""

	# Test parameters
	batch_size = 44
	sequence_nr = 1

	# Timing test parameters
	timing_test = True
	testbatches = 100

	#-------------------------

	# Define useful params
	from miprometheus.utils.param_interface import ParamInterface
	params = ParamInterface()
	tasks = ['Go','CompareColor']
	params.add_config_params({'data_folder': os.path.expanduser('~/data/cog'), 'root_folder': ' ', 'set': 'val', 'dataset_type': 'canonical','tasks': tasks})

	# Create problem - task Go
	cog_dataset = COGDataset(params)

	# Get a sample - Go
	sample = cog_dataset[0]
	print(repr(sample))

	# Test whether data structures match expected definitions
	assert sample['images'].shape == torch.ones((4,3,112,112)).shape
	assert sample['tasks'] == ['Go']
	assert sample['questions'] == ['point now beige u']
	assert sample['targets_reg'].shape == torch.ones((4,2)).shape
	assert len(sample['targets_class']) == 4
	assert sample['targets_class'][0] == ' '  

	# Get another sample - CompareColor
	sample2 = cog_dataset[1]
	print(repr(sample2))

	# Test whether data structures match expected definitions
	assert sample2['images'].shape == torch.ones((4,3,112,112)).shape
	assert sample2['tasks'] == ['CompareColor']
	assert sample2['questions'] == ['color of latest g equal color of last1 v ?']
	assert sample2['targets_reg'].shape == torch.ones((4,2)).shape
	assert len(sample2['targets_class']) == 4
	assert sample2['targets_class'][0] == 'invalid'  
	
	print('__getitem__ works')
	
	# Set up Dataloader iterator
	from torch.utils.data import DataLoader
	
	dataloader = DataLoader(dataset=cog_dataset, collate_fn=cog_dataset.collate_fn,
		            batch_size=batch_size, shuffle=False, num_workers=8)

	# Display single sample (0) from batch.
	batch = next(iter(dataloader))

	# Test whether batches are formed correctly	
	assert batch['images'].shape == torch.ones((batch_size,4,3,112,112)).shape
	assert len(batch['tasks']) == batch_size
	assert len(batch['questions']) == batch_size
	assert batch['targets_reg'].shape == torch.ones((batch_size,4,2)).shape
	assert len(batch['targets_class']) == batch_size
	assert len(batch['targets_class'][0]) == 4 

	# VQA expects 'targets', so change 'targets_class' to 'targets'
	# Implement a data_dict.pop later.
	batch['targets'] = batch['targets_reg']
	batch['targets_label'] = batch['targets_class']

	# Convert image to uint8
	batch['images'] = batch['images']/(np.iinfo(np.uint16).max)*255

	# Show sample - Task 1
	cog_dataset.show_sample(batch,0,sequence_nr)

	# Show sample - Task 2
	cog_dataset.show_sample(batch,1,sequence_nr)	

	print('Unit test completed')

	if timing_test:
		# Test speed of generating images vs preloading generated images.
		import time

		# Define params to load entire dataset - all tasks included
		params = ParamInterface()
		params.add_config_params({'data_folder': '/home/esevgen/IBM/cog-master', 'root_folder': ' ', 'set': 'val', 'dataset_type': 'canonical','tasks': 'all'})

		preload = time.time()
		full_cog_canonical = COGDataset(params)
		postload = time.time() 

		dataloader = DataLoader(dataset=full_cog_canonical, collate_fn=full_cog_canonical.collate_fn,
				          batch_size=batch_size, shuffle=True, num_workers=8)

		prebatch = time.time()
		for i, batch in enumerate(dataloader):
			if i == testbatches:
				break
			if i% 100 == 0:
				print('Batch # {} - {}'.format(i, type(batch)))
		postbatch = time.time()
	
		print('Number of workers: {}'.format(dataloader.num_workers))
		print('Time taken to load the dataset: {}s'.format(postload - preload))	
		print('Time taken to exhaust {} batches for a batch size of {} with image generation: {}s'.format(testbatches, 
													batch_size, postbatch-prebatch))
	
		# Test pregeneration and loading
		for i, batch in enumerate(dataloader):
			if i == testbatches:
				print('Finished saving {} batches'.format(testbatches))
				break
			if not os.path.exists(os.path.expanduser('~/data/COGtest')):
				os.makedirs(os.path.expanduser('~/data/COGtest'))
			np.save(os.path.expanduser('~/data/COGtest/'+str(i)),batch['images'])

		preload = time.time()
		for i in range(testbatches):
			mockload = np.fromfile(os.path.expanduser('~/data/COGtest/'+str(i)+'.npy'))
		postload = time.time()
		print('Generation time for {} batches: {}, Load time for {} batches: {}'.format(testbatches, postbatch-prebatch, 
												testbatches, postload-preload))

		print('Timing test completed, removing files.')
		for i in range(testbatches):
			os.remove(os.path.expanduser('~/data/COGtest/'+str(i)+'.npy'))
	
	print('Done!')
 
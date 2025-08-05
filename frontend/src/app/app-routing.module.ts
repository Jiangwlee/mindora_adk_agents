/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomePageComponent} from './components/home-page/home-page.component';
import {ChatbotPageComponent} from './components/chatbot-page/chatbot-page.component';
import {CustomPageComponent} from './components/custom-page/custom-page.component';
import {AdkDebugPageComponent} from './components/adk-debug-page/adk-debug-page.component';

const routes: Routes = [
  {
    path: '',
    component: HomePageComponent,
    title: 'AI Agent App Platform'
  },
  {
    path: 'app/chatbot/:name',
    component: ChatbotPageComponent,
    title: 'Chatbot App'
  },
  {
    path: 'app/custom/:name',
    component: CustomPageComponent,
    title: 'Custom App'
  },
  {
    path: 'adk-debug',
    component: AdkDebugPageComponent,
    title: 'ADK Debug Tool'
  },
  {
    path: '**',
    redirectTo: ''
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { 
    enableTracing: true,
    useHash: false,
    onSameUrlNavigation: 'reload'
  })],
  exports: [RouterModule],
})
export class AppRoutingModule {}

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

import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-adk-debug-page',
  template: `<app-chat></app-chat>`,
  standalone: false
})
export class AdkDebugPageComponent implements OnInit {
  
  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    // 确保有默认的查询参数以便 ChatComponent 能正常工作
    const currentParams = this.route.snapshot.queryParams;
    if (!currentParams['app']) {
      // 如果没有 app 参数，设置一个默认值或保持空白让用户选择
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { ...currentParams },
        queryParamsHandling: 'merge'
      });
    }
  }
}